import sqlite3
import os
import time
import threading

DB_PATH = "vault.db"
_lock = threading.Lock()

def get_connection():
    # check_same_thread=False allows FastAPI async workers to use the DB
    conn = sqlite3.connect(DB_PATH, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA secure_delete=ON;")
    return conn

def init_db():
    with get_connection() as conn:
        # 1. CORE CRYPTO VAULT (DO NOT CHANGE SCHEMA)
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
        conn.execute("CREATE INDEX IF NOT EXISTS idx_reaper ON vault_keys (status, expires_at);")

        # 2. PERSISTENT ADMIN CONFIG
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dlp_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                target_fields TEXT
            );
        """)
        conn.execute("INSERT OR IGNORE INTO dlp_config (id, target_fields) VALUES (1, 'sensitive_data');")


# --- CRYPTO OPERATIONS ---

def store_key(data_id: str, encrypted_dek: bytes, nonce: bytes, ttl_seconds: int = 10):
    now = int(time.time())
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO vault_keys (data_id, encrypted_dek, dek_nonce, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """, (data_id, encrypted_dek, nonce, now, now + ttl_seconds))

def get_key_metadata(data_id: str) -> dict:
    with get_connection() as conn:
        cursor = conn.execute("SELECT encrypted_dek, dek_nonce, status FROM vault_keys WHERE data_id = ?", (data_id,))
        row = cursor.fetchone()
        if row:
            return {"encrypted_dek": row["encrypted_dek"], "nonce": row["dek_nonce"], "status": row["status"]}
        return None

def shred_expired_keys() -> int:
    now = int(time.time())
    shredded_count = 0
    with get_connection() as conn:
        cursor = conn.execute("SELECT data_id FROM vault_keys WHERE status = 'ACTIVE' AND expires_at <= ?", (now,))
        for row in cursor.fetchall():
            data_id = row["data_id"]
            # Overwrite the DEK with random bytes before marking as shredded
            conn.execute("UPDATE vault_keys SET encrypted_dek = ?, status = 'SHREDDED', shredded_at = ? WHERE data_id = ?", 
                         (os.urandom(32), now, data_id))
            shredded_count += 1
    return shredded_count


# --- ADMIN CONFIG OPERATIONS ---

def get_config() -> list[str]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT target_fields FROM dlp_config WHERE id = 1")
        row = cursor.fetchone()
    
    if row is None or not row["target_fields"] or not row["target_fields"].strip():
        return ["sensitive_data"]
        
    return [f.strip() for f in row["target_fields"].split(",") if f.strip()]

def update_config(fields_string: str) -> list[str]:
    cleaned = [f.strip() for f in fields_string.split(",") if f.strip()]
    normalized = ", ".join(cleaned) if cleaned else "sensitive_data"
    
    with _lock:
        with get_connection() as conn:
            conn.execute(
                "UPDATE dlp_config SET target_fields = ? WHERE id = 1",
                (normalized,)
            )
    return get_config()
