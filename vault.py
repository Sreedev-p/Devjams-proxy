import sqlite3
import os
import time
import threading
import json

DB_PATH = "vault.db"
_lock = threading.Lock()


def get_connection():
    conn = sqlite3.connect(DB_PATH, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA secure_delete=ON;")
    conn.execute("PRAGMA busy_timeout=5000;")

    return conn


def init_db():
    with get_connection() as conn:
        # =========================================================
        # CORE CRYPTO VAULT
        # =========================================================
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vault_keys (
                data_id TEXT PRIMARY KEY,
                encrypted_dek BLOB NOT NULL,
                dek_nonce BLOB NOT NULL,
                purpose TEXT DEFAULT 'payload_protection',
                created_at INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                status TEXT DEFAULT 'ACTIVE',
                shredded_at INTEGER
            );
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_reaper
            ON vault_keys (status, expires_at);
        """)

        # =========================================================
        # ADMIN CONFIG
        # =========================================================
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dlp_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                target_fields TEXT
            );
        """)

        conn.execute("""
            INSERT OR IGNORE INTO dlp_config (id, target_fields)
            VALUES (1, 'sensitive_data');
        """)

        # =========================================================
        # IMMUTABLE AUDIT LOG
        # =========================================================
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                data_id TEXT,
                details TEXT
            );
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp
            ON audit_logs (timestamp DESC);
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_event_type
            ON audit_logs (event_type, timestamp DESC);
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_data_id
            ON audit_logs (data_id, timestamp DESC);
        """)

        # Make audit log append-only
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS trg_audit_no_update
            BEFORE UPDATE ON audit_logs
            BEGIN
                SELECT RAISE(ABORT, 'audit_logs is append-only');
            END;
        """)

        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS trg_audit_no_delete
            BEFORE DELETE ON audit_logs
            BEGIN
                SELECT RAISE(ABORT, 'audit_logs is append-only');
            END;
        """)


def log_event(event_type: str, data_id: str | None = None, details=None):
    ts = int(time.time())

    if details is None:
        serialized = "{}"
    elif isinstance(details, str):
        serialized = details
    else:
        serialized = json.dumps(details)

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO audit_logs (timestamp, event_type, data_id, details)
            VALUES (?, ?, ?, ?)
        """, (ts, event_type, data_id, serialized))


# =========================================================
# CRYPTO OPERATIONS
# =========================================================
def store_key(data_id: str, encrypted_dek: bytes, nonce: bytes, ttl_seconds: int = 10):
    now = int(time.time())
    expires_at = now + ttl_seconds

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO vault_keys (data_id, encrypted_dek, dek_nonce, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """, (data_id, encrypted_dek, nonce, now, expires_at))

    log_event(
        "KEY_GENERATED",
        data_id,
        {
            "ttl_seconds": ttl_seconds,
            "created_at": now,
            "expires_at": expires_at,
            "status": "ACTIVE"
        }
    )


def get_key_metadata(data_id: str) -> dict | None:
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT encrypted_dek, dek_nonce, status, expires_at, shredded_at
            FROM vault_keys
            WHERE data_id = ?
        """, (data_id,))
        row = cursor.fetchone()

    if row:
        log_event(
            "DECRYPTION_ATTEMPT",
            data_id,
            {
                "status": row["status"],
                "expires_at": row["expires_at"],
                "shredded_at": row["shredded_at"]
            }
        )

        return {
            "encrypted_dek": row["encrypted_dek"],
            "nonce": row["dek_nonce"],
            "status": row["status"],
            "expires_at": row["expires_at"],
            "shredded_at": row["shredded_at"]
        }

    log_event(
        "DECRYPTION_ATTEMPT",
        data_id,
        {
            "status": "MISSING",
            "message": "No key metadata found"
        }
    )
    return None


def shred_expired_keys() -> int:
    now = int(time.time())
    shredded_count = 0

    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT data_id, expires_at
            FROM vault_keys
            WHERE status = 'ACTIVE' AND expires_at <= ?
        """, (now,))
        expired_rows = cursor.fetchall()

        for row in expired_rows:
            data_id = row["data_id"]
            expires_at = row["expires_at"]

            conn.execute("""
                UPDATE vault_keys
                SET encrypted_dek = ?, status = 'SHREDDED', shredded_at = ?
                WHERE data_id = ?
            """, (os.urandom(32), now, data_id))

            shredded_count += 1

            log_event(
                "KEY_SHREDDED",
                data_id,
                {
                    "expires_at": expires_at,
                    "shredded_at": now,
                    "status": "SHREDDED"
                }
            )

    return shredded_count


def get_key_counts() -> dict:
    with get_connection() as conn:
        active = conn.execute("""
            SELECT COUNT(*) AS count
            FROM vault_keys
            WHERE status = 'ACTIVE'
        """).fetchone()["count"]

        shredded = conn.execute("""
            SELECT COUNT(*) AS count
            FROM vault_keys
            WHERE status = 'SHREDDED'
        """).fetchone()["count"]

    return {
        "active_keys": active,
        "shredded_keys": shredded
    }


def get_audit_logs(limit: int = 200) -> list[dict]:
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT id, timestamp, event_type, data_id, details
            FROM audit_logs
            ORDER BY timestamp DESC, id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()

    results = []
    for row in rows:
        details = row["details"]
        try:
            details = json.loads(details) if details else {}
        except (json.JSONDecodeError, TypeError):
            pass

        results.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "event_type": row["event_type"],
            "data_id": row["data_id"],
            "details": details
        })

    return results


def get_audit_summary() -> dict:
    with get_connection() as conn:
        decrypt_attempts = conn.execute("""
            SELECT COUNT(*) AS count
            FROM audit_logs
            WHERE event_type = 'DECRYPTION_ATTEMPT'
        """).fetchone()["count"]

        total_events = conn.execute("""
            SELECT COUNT(*) AS count
            FROM audit_logs
        """).fetchone()["count"]

    counts = get_key_counts()
    counts["decryption_attempts"] = decrypt_attempts
    counts["total_events"] = total_events
    return counts


# =========================================================
# ADMIN CONFIG OPERATIONS
# =========================================================
def get_config() -> list[str]:
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT target_fields
            FROM dlp_config
            WHERE id = 1
        """)
        row = cursor.fetchone()

    if row is None or not row["target_fields"] or not row["target_fields"].strip():
        return ["sensitive_data"]

    return [f.strip() for f in row["target_fields"].split(",") if f.strip()]


def update_config(fields_string: str) -> list[str]:
    cleaned = [f.strip() for f in fields_string.split(",") if f.strip()]
    normalized = ", ".join(cleaned) if cleaned else "sensitive_data"

    with _lock:
        with get_connection() as conn:
            conn.execute("""
                UPDATE dlp_config
                SET target_fields = ?
                WHERE id = 1
            """, (normalized,))

    active_fields = get_config()

    log_event(
        "CONFIG_UPDATED",
        None,
        {
            "active_fields": active_fields
        }
    )

    return active_fields
