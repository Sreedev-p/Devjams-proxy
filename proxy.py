import json
import uuid
import asyncio
import os
from contextlib import asynccontextmanager
from typing import Optional

import httpx
from fastapi import FastAPI, Request, HTTPException, Response, Header, Depends
from fastapi.middleware.cors import CORSMiddleware

import vault
import crypto_engine
from reaper import run_reaper

TARGET_BACKEND = os.getenv("TARGET_BACKEND", "https://bd2dfb593379b0.lhr.life")
DEFAULT_TARGET_FIELDS = {"sensitive_data"}
ADMIN_API_KEY = os.getenv("DATAEXPIRY_ADMIN_KEY", "supersecretadmin")


@asynccontextmanager
async def lifespan(app: FastAPI):
    vault.init_db()
    reaper_task = asyncio.create_task(run_reaper(interval_seconds=2))
    try:
        yield
    finally:
        reaper_task.cancel()


app = FastAPI(lifespan=lifespan, title="DataExpiry Reverse Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_target_fields() -> set[str]:
    fields = vault.get_config()
    return set(fields) if fields else DEFAULT_TARGET_FIELDS


def verify_admin(x_admin_key: Optional[str] = Header(default=None, alias="X-Admin-Key")):
    if not x_admin_key:
        raise HTTPException(status_code=401, detail="Missing Admin Key")
    if x_admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid Admin Key")
    return True


def process_outgoing_payload(data, ttl_seconds=10):
    active_fields = get_target_fields()

    if isinstance(data, dict):
        for k, v in data.items():
            if k in active_fields and isinstance(v, str):
                data_id = str(uuid.uuid4())
                dek = crypto_engine.generate_dek()
                b64_nonce, b64_cipher = crypto_engine.encrypt_payload(v, dek)

                enc_dek, dek_nonce = crypto_engine.wrap_dek(dek)
                vault.store_key(data_id, enc_dek, dek_nonce, ttl_seconds=ttl_seconds)

                data[k] = f"ENC::{data_id}::{b64_nonce}::{b64_cipher}"

            elif isinstance(v, (dict, list)):
                process_outgoing_payload(v, ttl_seconds)

    elif isinstance(data, list):
        for item in data:
            process_outgoing_payload(item, ttl_seconds)

    return data


def process_incoming_payload(data):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str) and v.startswith("ENC::"):
                parts = v.split("::")
                if len(parts) == 4:
                    _, data_id, b64_nonce, b64_cipher = parts
                    meta = vault.get_key_metadata(data_id)

                    if not meta:
                        continue

                    if meta["status"] == "SHREDDED":
                        raise HTTPException(
                            status_code=410,
                            detail={
                                "error": "Data Expired",
                                "detail": "Decryption key has been cryptographically erased."
                            }
                        )

                    dek = crypto_engine.unwrap_dek(meta["encrypted_dek"], meta["nonce"])
                    data[k] = crypto_engine.decrypt_payload(b64_cipher, b64_nonce, dek)

            elif isinstance(v, (dict, list)):
                process_incoming_payload(v)

    elif isinstance(data, list):
        for item in data:
            process_incoming_payload(item)

    return data


@app.get("/api/admin/config")
async def admin_get_config():
    return {"active_fields": vault.get_config()}


@app.post("/api/admin/config", dependencies=[Depends(verify_admin)])
async def admin_update_config(request: Request):
    body = await request.json()
    fields = body.get("fields", "")
    active_fields = vault.update_config(fields)
    return {"status": "ok", "active_fields": active_fields}


@app.get("/api/admin/logs", dependencies=[Depends(verify_admin)])
async def admin_get_logs(limit: int = 200):
    logs = vault.get_audit_logs(limit=limit)
    summary = vault.get_audit_summary()
    return {"summary": summary, "logs": logs}


@app.get("/api/admin/stats", dependencies=[Depends(verify_admin)])
async def admin_get_stats():
    return vault.get_audit_summary()


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_traffic(request: Request, path: str):
    url = f"{TARGET_BACKEND}/{path}"
    body = b""

    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            json_body = await request.json()
            custom_ttl = int(json_body.get("ttl_seconds", 10))
            processed_body = process_outgoing_payload(json_body, custom_ttl)
            body = json.dumps(processed_body).encode("utf-8")
        except (json.JSONDecodeError, ValueError, TypeError):
            body = await request.body()

    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params
            )
        except httpx.ConnectError:
            raise HTTPException(status_code=502, detail="Dummy backend is offline.")

    try:
        resp_json = resp.json()
        decrypted = process_incoming_payload(resp_json)
        return Response(
            content=json.dumps(decrypted),
            status_code=resp.status_code,
            media_type="application/json"
        )
    except json.JSONDecodeError:
        filtered_headers = dict(resp.headers)
        filtered_headers.pop("content-length", None)
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=filtered_headers
        )
