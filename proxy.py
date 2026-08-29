# proxy.py
import json
import uuid
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Response
import httpx
from fastapi.middleware.cors import CORSMiddleware

import vault
import crypto_engine
from reaper import run_reaper

# Configuration
TARGET_BACKEND = "http://localhost:5000"  # Points to dummy_app/server.py
TARGET_FIELDS = {"sensitive_data"} # Fields to crypto-shred

@asynccontextmanager
async def lifespan(app: FastAPI):
    vault.init_db()
    # Start the Reaper daemon. It checks for expired keys every 2 seconds.
    reaper_task = asyncio.create_task(run_reaper(interval_seconds=2))
    yield 
    reaper_task.cancel()

app = FastAPI(lifespan=lifespan, title="DataExpiry Reverse Proxy")

def process_outgoing_payload(data, ttl_seconds=10):
    """Recursively scans JSON to encrypt sensitive fields before sending upstream."""
    if isinstance(data, dict):
        for k, v in data.items():
            if k in TARGET_FIELDS and isinstance(v, str):
                data_id = str(uuid.uuid4())
                dek = crypto_engine.generate_dek()
                b64_nonce, b64_cipher = crypto_engine.encrypt_payload(v, dek)
                
                enc_dek, dek_nonce = crypto_engine.wrap_dek(dek)
                # Apply the dynamic TTL received from the frontend
                vault.store_key(data_id, enc_dek, dek_nonce, ttl_seconds=ttl_seconds) 
                
                data[k] = f"ENC::{data_id}::{b64_nonce}::{b64_cipher}"
            elif isinstance(v, (dict, list)):
                process_outgoing_payload(v, ttl_seconds)
    elif isinstance(data, list):
        for item in data:
            process_outgoing_payload(item, ttl_seconds)
    return data

def process_incoming_payload(data):
    """Scans JSON returning from upstream to decrypt envelopes."""
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str) and v.startswith("ENC::"):
                parts = v.split("::")
                if len(parts) == 4:
                    _, data_id, b64_nonce, b64_cipher = parts
                    meta = vault.get_key_metadata(data_id)
                    
                    if not meta:
                        continue 
                        
                    # THE KILL SWITCH: 410 Gone
                    if meta["status"] == "SHREDDED":
                        raise HTTPException(
                            status_code=410, 
                            detail={
                                "error": "Data Expired", 
                                "message": f"Cryptographic Erasure confirmed. Key for '{k}' has been shredded."
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

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_traffic(request: Request, path: str):
    url = f"{TARGET_BACKEND}/{path}"
    
    body = b""
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            json_body = await request.json()
            # Extract the TTL from the UI payload, defaulting to 10 if missing
            custom_ttl = json_body.get("ttl_seconds", 10)
            
            processed_body = process_outgoing_payload(json_body, custom_ttl)
            body = json.dumps(processed_body).encode("utf-8")
        except json.JSONDecodeError:
            body = await request.body()
            

    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                method=request.method, url=url, headers=headers, content=body, params=request.query_params
            )
        except httpx.ConnectError:
            raise HTTPException(status_code=502, detail="Dummy backend is offline.")
    
    try:
        resp_json = resp.json()
        return process_incoming_payload(resp_json)
    except json.JSONDecodeError:
        return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))