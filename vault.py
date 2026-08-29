import sqlite3
import threading

DB_FILE = "vault.db"
_lock = threading.Lock()

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Existing key_vault table stays untouched
    cur.execute("""
        CREATE TABLE IF NOT EXISTS key_vault (
            id TEXT PRIMARY KEY,
            wrapped_key BLOB,
            status TEXT,
            expires_at REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dlp_config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            target_fields TEXT
        )
    """)

    cur.execute("""
        INSERT OR IGNORE INTO dlp_config (id, target_fields) VALUES (1, 'sensitive_data')
    """)

    conn.commit()
    conn.close()


def get_config() -> list[str]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT target_fields FROM dlp_config WHERE id = 1")
    row = cur.fetchone()
    conn.close()

    if row is None or not row["target_fields"] or not row["target_fields"].strip():
        return ["sensitive_data"]

    return [f.strip() for f in row["target_fields"].split(",") if f.strip()]


def update_config(fields_string: str) -> list[str]:
    cleaned = [f.strip() for f in fields_string.split(",") if f.strip()]
    normalized = ", ".join(cleaned) if cleaned else "sensitive_data"

    with _lock:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE dlp_config SET target_fields = ? WHERE id = 1",
            (normalized,)
        )
        conn.commit()
        conn.close()

    return get_config()
