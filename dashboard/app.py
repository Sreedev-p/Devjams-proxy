import streamlit as st
import requests
import time
import base64
from pathlib import Path

# --- Configuration ---
st.set_page_config(page_title="DataExpiry Demo", layout="wide")

# --- CUSTOM THEME (CSS INJECTION) - LIGHT "TEAK-STYLE" REDESIGN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Manrope:wght@400;500;600;700&display=swap');

    /* Light off-white background with subtle dot grid, like the reference site */
    [data-testid="stAppViewContainer"] {
        background-color: #FAFAF7;
        background-image: radial-gradient(circle, #E6E4DE 1px, transparent 1px);
        background-size: 22px 22px;
    }

    [data-testid="stAppViewContainer"] > .main {
        position: relative;
        z-index: 1;
    }

    [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0);
    }

    /* Global font sizing */
    .stApp {
        font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 16px !important;
        letter-spacing: -0.1px;
        color: #14140F !important;
    }

    .stApp h1 {
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -1.2px;
        font-size: 2.5rem !important;
        margin-bottom: 1.5rem !important;
        color: #14140F !important;
    }

    .stApp h2 {
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.8px;
        font-size: 1.75rem !important;
        margin-bottom: 1rem !important;
        color: #14140F !important;
    }

    .stApp h3 {
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
        font-size: 1.25rem !important;
        color: #14140F !important;
    }

    /* Input fields */
    .stTextInput input {
        font-size: 14px !important;
        font-family: 'Manrope', sans-serif !important;
        padding: 10px 12px !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E2E0D9 !important;
        border-radius: 8px !important;
        color: #14140F !important;
    }

    .stSelectbox {
        font-size: 14px !important;
    }

    .stSelectbox > div > div {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E0D9 !important;
        border-radius: 8px !important;
    }

    /* Buttons - yellow pill, like the reference "Book a demo" button */
    .stButton button {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.2px;
        font-size: 14px !important;
        padding: 10px 20px !important;
        background-color: #F5D033 !important;
        color: #14140F !important;
        border: none !important;
        border-radius: 999px !important;
        box-shadow: none !important;
        transition: transform 0.15s ease, background-color 0.15s ease;
    }

    .stButton button:hover {
        background-color: #E8C11F !important;
        color: #14140F !important;
        transform: translateY(-1px);
    }

    .stButton button:active {
        background-color: #D9B310 !important;
    }

    /* Alerts & Messages */
    div[data-testid="stAlert"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E0D9;
        border-radius: 10px;
        padding: 16px !important;
        font-size: 14px !important;
        color: #14140F !important;
    }

    /* Sidebar specific */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E0D9;
    }

    [data-testid="stSidebar"] .stTextInput input {
        font-size: 13px !important;
    }

    [data-testid="stSidebar"] .stMarkdownContainer {
        font-size: 14px !important;
        color: #14140F !important;
    }

    [data-testid="stSidebar"] h2 {
        font-size: 1.5rem !important;
    }

    /* Divider */
    hr {
        margin: 2rem 0 !important;
        border-color: #E2E0D9 !important;
    }

    /* JSON display */
    .stJson {
        font-size: 13px !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E2E0D9 !important;
        border-radius: 8px !important;
    }

    /* Cards for columns (subheaders act as section headers) */
    .stColumn {
        background-color: transparent;
    }

    /* Captions */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #6B6A63 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ DataExpiry: Zero-Code Cryptographic Erasure")

# dashboard/app.py (around line 8)
PROXY_URL = "https://56d2bcc776805b.lhr.life"
BACKEND_URL = "https://353bd044ed9e1d.lhr.life"

# =========================================================
# SIDEBAR: Enterprise DLP Admin Config Panel
# =========================================================
with st.sidebar:
    st.header("⚙️ Enterprise DLP Config")

    st.caption("Configure which JSON fields the proxy encrypts on the fly. Changes are saved permanently in the SQLite vault and apply immediately, no restart needed.")

    admin_key = st.text_input("Admin API Key", type="password", key="admin_key_input")
    target_fields = st.text_input("Fields to Encrypt (comma-separated)", "sensitive_data", key="target_fields_input")

    if st.button("Apply Security Policies"):
        headers = {"X-Admin-Key": admin_key}
        payload = {"fields": target_fields}
        try:
            res = requests.post(f"{PROXY_URL}/api/admin/config", json=payload, headers=headers)
            if res.status_code in [200, 201]:
                st.success(f"Active fields: {res.json().get('active_fields')}")
            elif res.status_code == 401:
                st.error("Invalid Admin Key!")
            else:
                st.error(f"Unexpected error: {res.status_code} - {res.text}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach proxy — is it running?")

    st.divider()

    # Read-only live view of current active fields (no auth required)
    if st.button("🔄 View Current Active Fields"):
        try:
            cfg_res = requests.get(f"{PROXY_URL}/api/admin/config")
            if cfg_res.status_code == 200:
                st.info(f"Currently encrypting: {cfg_res.json().get('active_fields')}")
            else:
                st.warning(f"Could not fetch config: {cfg_res.status_code}")
        except requests.exceptions.ConnectionError:
            st.warning("Proxy unreachable.")

# --- Main Split-Screen UI ---
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
            res = requests.post(f"{PROXY_URL}/api/records", json=payload)
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
            db_res = requests.get(f"{BACKEND_URL}/api/records")
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

# --- Live Expiry & Retrieval Demo ---
if "expiry_time" in st.session_state and "last_record_id" in st.session_state:
    st.subheader("⏱️ Live Expiry & Retrieval Test")

    st.button("🔄 Refresh Timer")

    remaining = int(st.session_state["expiry_time"] - time.time())

    if remaining > 0:
        st.warning(f"Key TTL active: {remaining}s remaining before cryptographic shredding...")
    else:
        st.error("TTL expired! Cryptographic key has been mathematically shredded in the Vault.")

    if st.button("Attempt Decrypted Read via Proxy"):
        rec_id = st.session_state["last_record_id"]
        try:
            fetch_res = requests.get(f"{PROXY_URL}/api/records/{rec_id}")

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
