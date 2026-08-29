import sqlite3
import os
import time

DB_PATH = "vault.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA secure_delete=ON;")
    return conn

def init_db():
    with get_connection() as conn:
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
        return {"encrypted_dek": row[0], "nonce": row[1], "status": row[2]} if row else None

def shred_expired_keys() -> int:
    now = int(time.time())
    shredded_count = 0
    with get_connection() as conn:
        cursor = conn.execute("SELECT data_id FROM vault_keys WHERE status = 'ACTIVE' AND expires_at <= ?", (now,))
        for data_id in [row[0] for row in cursor.fetchall()]:
            conn.execute("UPDATE vault_keys SET encrypted_dek = ?, status = 'SHREDDED', shredded_at = ? WHERE data_id = ?", (os.urandom(32), now, data_id))
            shredded_count += 1
    return shredded_count
