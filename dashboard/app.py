import streamlit as st
import requests
import time
import base64
import json
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="DataExpiry Demo", layout="wide")

BG_IMAGE_PATH = "cyber-background-8k.png"


@st.cache_data
def get_base64_image(image_path):
    path = Path(image_path)
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


bg_base64 = get_base64_image(BG_IMAGE_PATH)

if bg_base64:
    bg_css = f"""
        background-image: url("data:image/png;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    """
else:
    bg_css = "background-color: #000000;"


st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Manrope:wght@400;500;600;700&display=swap');

    [data-testid="stAppViewContainer"] {{
        {bg_css}
    }}

    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        inset: 0;
        background-color: rgba(0, 0, 0, 0.45);
        z-index: 0;
        pointer-events: none;
    }}

    [data-testid="stAppViewContainer"] > .main {{
        position: relative;
        z-index: 1;
    }}

    [data-testid="stHeader"] {{
        background-color: rgba(0, 0, 0, 0);
    }}

    .stApp {{
        font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 16px !important;
        letter-spacing: -0.1px;
    }}

    .stApp h1 {{
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -1.2px;
        font-size: 2.5rem !important;
        margin-bottom: 1.5rem !important;
    }}

    .stApp h2 {{
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.8px;
        font-size: 1.75rem !important;
        margin-bottom: 1rem !important;
    }}

    .stApp h3 {{
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
        font-size: 1.25rem !important;
    }}

    .stTextInput input {{
        font-size: 14px !important;
        font-family: 'Manrope', sans-serif !important;
        padding: 10px 12px !important;
    }}

    .stSelectbox {{
        font-size: 14px !important;
    }}

    .stButton button {{
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.2px;
        font-size: 14px !important;
        padding: 10px 20px !important;
    }}

    div[data-testid="stAlert"] {{
        background-color: rgba(17, 17, 17, 0.85);
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 16px !important;
        font-size: 14px !important;
    }}

    [data-testid="stSidebar"] {{
        background-color: rgba(17, 17, 17, 0.9);
    }}

    [data-testid="stSidebar"] .stTextInput input {{
        font-size: 13px !important;
    }}

    [data-testid="stSidebar"] .stMarkdownContainer {{
        font-size: 14px !important;
    }}

    [data-testid="stSidebar"] h2 {{
        font-size: 1.5rem !important;
    }}

    .soc-card {{
        background: rgba(18, 18, 18, 0.78);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 16px;
    }}

    .small-muted {{
        color: #bdbdbd;
        font-size: 13px;
    }}

    .stJson {{
        font-size: 13px !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ DataExpiry: Zero-Code Cryptographic Erasure")

PROXY_URL = "https://6e3319dd2e30ff.lhr.life"
BACKEND_URL = "https://bd2dfb593379b0.lhr.life"


def format_ts(ts):
    try:
        return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)


def fetch_soc_logs(admin_key: str, limit: int = 200):
    headers = {"X-Admin-Key": admin_key}
    return requests.get(
        f"{PROXY_URL}/api/admin/logs",
        headers=headers,
        params={"limit": limit},
        timeout=10
    )


with st.sidebar:
    st.header("⚙️ Enterprise DLP Config")

    st.caption("Configure which JSON fields the proxy encrypts on the fly. Changes are saved permanently in the SQLite vault and apply immediately, no restart needed.")

    admin_key = st.text_input("Admin API Key", type="password", key="admin_key_input")
    target_fields = st.text_input("Fields to Encrypt (comma-separated)", "sensitive_data", key="target_fields_input")

    if st.button("Apply Security Policies"):
        headers = {"X-Admin-Key": admin_key}
        payload = {"fields": target_fields}
        try:
            res = requests.post(f"{PROXY_URL}/api/admin/config", json=payload, headers=headers, timeout=10)
            if res.status_code in [200, 201]:
                st.success(f"Active fields: {res.json().get('active_fields')}")
            elif res.status_code == 401:
                st.error("Invalid Admin Key!")
            else:
                st.error(f"Unexpected error: {res.status_code} - {res.text}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach proxy — is it running?")

    st.divider()

    if st.button("🔄 View Current Active Fields"):
        try:
            cfg_res = requests.get(f"{PROXY_URL}/api/admin/config", timeout=10)
            if cfg_res.status_code == 200:
                st.info(f"Currently encrypting: {cfg_res.json().get('active_fields')}")
            else:
                st.warning(f"Could not fetch config: {cfg_res.status_code}")
        except requests.exceptions.ConnectionError:
            st.warning("Proxy unreachable.")


tab_live, tab_soc = st.tabs(["🔌 Live Routing", "🛡️ SOC Dashboard"])


with tab_live:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 Client / Application View")
        user_name = st.text_input("Customer Name", "Alice Smith")
        sensitive_data = st.text_input("Sensitive Data (e.g. Card / SSN)", "4532-xxxx-xxxx-8891")

        ttl_options = {
            "15 Seconds (Live Pitch Demo)": 15,
            "30 Seconds (Standard Demo)": 30,
            "1 Hour (Temporary Cache)": 3600,
            "24 Hours (Daily Rotation)": 86400,
            "30 Days (Standard Compliance)": 2592000,
            "1 Year (Enterprise Archival)": 31536000
        }
        selected_ttl = st.selectbox("Data Retention Policy (Time-To-Live)", list(ttl_options.keys()))
        ttl = ttl_options[selected_ttl]

        if st.button("Submit Sensitive Data"):
            payload = {
                "user_name": user_name,
                "sensitive_data": sensitive_data,
                "ttl_seconds": ttl
            }
            try:
                res = requests.post(f"{PROXY_URL}/api/records", json=payload, timeout=10)
                if res.status_code in [200, 201]:
                    st.session_state["last_record_id"] = res.json().get("id")
                    st.session_state["expiry_time"] = time.time() + ttl
                    st.success(f"Data routed through Proxy with a {selected_ttl} retention policy!")
                else:
                    st.error(f"Proxy Error: {res.status_code} - {res.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to Proxy! (Check if port 8000 is running).")

    with col2:
        st.subheader("🕵️ Hacker View (Target Database)")
        st.info("Live peek inside `company_database.db`:")

        if st.button("Refresh Database View"):
            try:
                db_res = requests.get(f"{BACKEND_URL}/api/records", timeout=10)
                if db_res.status_code == 200:
                    records = db_res.json()
                    if records:
                        st.json(records)
                    else:
                        st.write("Database is currently empty.")
                else:
                    st.error("Failed to read database.")
            except requests.exceptions.ConnectionError:
                st.warning("Target backend (port 5000) is not running.")

    st.divider()

    if "expiry_time" in st.session_state and "last_record_id" in st.session_state:
        st.subheader("⏱️ Live Expiry & Retrieval Test")

        timer_placeholder = st.empty()

        if st.button("Attempt Decrypted Read via Proxy"):
            rec_id = st.session_state["last_record_id"]
            try:
                fetch_res = requests.get(f"{PROXY_URL}/api/records/{rec_id}", timeout=10)

                if fetch_res.status_code == 200:
                    st.success("200 OK: Key active. Decrypted plaintext restored.")
                    st.json(fetch_res.json())
                elif fetch_res.status_code == 410:
                    st.error("410 Gone: Decryption key permanently erased from Vault.")
                    st.json(fetch_res.json())
                else:
                    st.warning(f"Unexpected Proxy response: {fetch_res.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to Proxy for retrieval.")

        remaining = int(st.session_state["expiry_time"] - time.time())

        if remaining > 0:
            if remaining <= 60:
                while remaining > 0:
                    timer_placeholder.warning(f"⏳ **LIVE COUNTDOWN:** `{remaining}s` remaining before cryptographic shredding...")
                    time.sleep(1)
                    remaining = int(st.session_state["expiry_time"] - time.time())
                timer_placeholder.error("🚨 **TTL EXPIRED:** Cryptographic key has been mathematically shredded in the Vault.")
            else:
                timer_placeholder.warning(f"⏳ **KEY ACTIVE:** `{remaining:,}s` remaining before cryptographic shredding...")
        else:
            timer_placeholder.error("🚨 **TTL EXPIRED:** Cryptographic key has been mathematically shredded in the Vault.")


with tab_soc:
    st.subheader("🛡️ SOC Dashboard")
    st.caption("Immutable defensive telemetry for encryption, decryption attempts, config changes, and cryptographic shredding events.")

    if not admin_key:
        st.warning("Enter the Admin API Key in the sidebar to unlock the SOC dashboard.")
    else:
        c1, c2, c3 = st.columns([1, 1, 1])
        refresh = c3.button("🔄 Refresh SOC Telemetry")

        if refresh or "soc_loaded" not in st.session_state:
            st.session_state["soc_loaded"] = True

        try:
            logs_res = fetch_soc_logs(admin_key, limit=250)

            if logs_res.status_code == 200:
                payload = logs_res.json()
                summary = payload.get("summary", {})
                logs = payload.get("logs", [])

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Active Keys", summary.get("active_keys", 0))
                m2.metric("Shredded Keys", summary.get("shredded_keys", 0))
                m3.metric("Decryption Attempts", summary.get("decryption_attempts", 0))
                m4.metric("Total Events", summary.get("total_events", 0))

                formatted_logs = []
                for row in logs:
                    details = row.get("details", {})
                    if not isinstance(details, str):
                        details = json.dumps(details)
                    formatted_logs.append({
                        "id": row.get("id"),
                        "timestamp": format_ts(row.get("timestamp")),
                        "event_type": row.get("event_type"),
                        "data_id": row.get("data_id"),
                        "details": details
                    })

                st.markdown("### Event Stream")
                st.dataframe(
                    formatted_logs,
                    use_container_width=True,
                    hide_index=True,
                    height=420
                )

            elif logs_res.status_code == 401:
                st.error("Invalid Admin Key. SOC telemetry is restricted.")
            else:
                st.error(f"Failed to load SOC telemetry: {logs_res.status_code} - {logs_res.text}")

        except requests.exceptions.ConnectionError:
            st.error("Cannot reach proxy for SOC telemetry.")
        except requests.exceptions.Timeout:
            st.error("SOC telemetry request timed out.")
