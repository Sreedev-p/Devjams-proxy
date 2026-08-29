import streamlit as st
import requests
import time
import base64
from pathlib import Path

# --- Configuration ---
st.set_page_config(page_title="DataExpiry Demo", layout="wide", initial_sidebar_state="collapsed")

# --- THEME DETECTION ---
try:
    dark_mode = st.context.theme.type == "dark"
except Exception:
    dark_mode = False

# --- Color tokens ---
if dark_mode:
    THEME = {
        "bg": "#0B0B09",
        "dot": "rgba(255, 255, 255, 0.055)",
        "text": "#F3F2EC",
        "muted": "#A6A497",
        "surface": "#151512",
        "surface_alt": "#1B1B17",
        "border": "#2C2B24",
        "sidebar_bg": "#101210",
        "accent": "#F5D033",
        "accent_hover": "#FFDE66",
        "accent_active": "#E0BC24",
        "accent_text": "#14140F",
        "button_shadow": "0 0 0 1px rgba(245, 208, 51, 0.12), 0 6px 20px rgba(245, 208, 51, 0.16)",
        "button_shadow_hover": "0 0 0 1px rgba(245, 208, 51, 0.2), 0 8px 26px rgba(245, 208, 51, 0.26)",
        "card_shadow": "inset 0 1px 0 rgba(255, 255, 255, 0.04), 0 8px 24px rgba(0, 0, 0, 0.35)",
    }
else:
    THEME = {
        "bg": "#FAFAF7",
        "dot": "#E6E4DE",
        "text": "#14140F",
        "muted": "#6B6A63",
        "surface": "#FFFFFF",
        "surface_alt": "#F4F3EE",
        "border": "#E2E0D9",
        "sidebar_bg": "#FFFFFF",
        "accent": "#F5D033",
        "accent_hover": "#E8C11F",
        "accent_active": "#D9B310",
        "accent_text": "#14140F",
        "button_shadow": "none",
        "button_shadow_hover": "none",
        "card_shadow": "0 1px 2px rgba(20, 20, 15, 0.04)",
    }

# --- CUSTOM THEME (CSS INJECTION) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    [data-testid="stAppViewContainer"] {{
        background-color: {THEME["bg"]};
        background-image: radial-gradient(circle, {THEME["dot"]} 1px, transparent 1px);
        background-size: 22px 22px;
    }}

    [data-testid="stAppViewContainer"] > .main {{ position: relative; z-index: 1; }}
    [data-testid="stHeader"] {{ background-color: rgba(0, 0, 0, 0); }}

    .stApp {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 16px !important;
        color: {THEME["text"]} !important;
    }}

    .stApp h1, .stApp h2, .stApp h3 {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: {THEME["text"]} !important;
    }}

    .stTextInput input {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: {THEME["surface"]} !important;
        border: 1px solid {THEME["border"]} !important;
        border-radius: 8px !important;
        color: {THEME["text"]} !important;
        box-shadow: {THEME["card_shadow"]};
    }}

    .stTextInput input:focus {{ border-color: {THEME["accent"]} !important; }}

    .stSelectbox > div > div {{
        background-color: {THEME["surface"]} !important;
        border: 1px solid {THEME["border"]} !important;
        border-radius: 8px !important;
        color: {THEME["text"]} !important;
    }}

    .stButton button {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        background-color: {THEME["accent"]} !important;
        color: {THEME["accent_text"]} !important;
        border-radius: 999px !important;
        box-shadow: {THEME["button_shadow"]};
        transition: all 0.15s ease;
    }}

    .stButton button:hover {{
        background-color: {THEME["accent_hover"]} !important;
        box-shadow: {THEME["button_shadow_hover"]};
        transform: translateY(-1px);
    }}

    div[data-testid="stAlert"] {{
        background-color: {THEME["surface"]};
        border: 1px solid {THEME["border"]};
        border-radius: 10px;
        color: {THEME["text"]} !important;
        box-shadow: {THEME["card_shadow"]};
    }}

    hr {{ border-color: {THEME["border"]} !important; }}

    .stJson, .stDataFrame {{
        font-family: 'JetBrains Mono', monospace !important;
        background-color: {THEME["surface_alt"]} !important;
        border-radius: 8px !important;
        box-shadow: {THEME["card_shadow"]};
    }}

    .st-key-view_selector div[role="radiogroup"] {{
        display: inline-flex;
        gap: 4px;
        background-color: {THEME["surface_alt"]};
        border: 1px solid {THEME["border"]};
        border-radius: 999px;
        padding: 4px;
    }}

    .st-key-view_selector label > div:first-child {{ display: none !important; }}

    .st-key-view_selector label > div:last-child {{
        padding: 10px 22px !important;
        border-radius: 999px !important;
        font-weight: 700 !important;
        color: {THEME["muted"]} !important;
    }}

    .st-key-view_selector label:hover > div:last-child {{ color: {THEME["text"]} !important; }}

    .st-key-view_selector label:has(input:checked) > div:last-child {{
        background-color: {THEME["accent"]} !important;
        color: {THEME["accent_text"]} !important;
        box-shadow: {THEME["button_shadow"]};
    }}

    .st-key-view_panel > div[data-testid="stVerticalBlockBorderWrapper"],
    .st-key-expiry_panel > div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {THEME["surface"]} !important;
        border: 1px solid {THEME["border"]} !important;
        border-radius: 18px !important;
        box-shadow: {THEME["card_shadow"]};
        padding: 1.75rem !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ DataExpiry: Zero-Code Cryptographic Erasure")

PROXY_URL = "https://latrine-primal-retired.ngrok-free.dev"
BACKEND_URL = "https://thirty-plants-boil.loca.lt"

# RESTORED BYPASS HEADERS
TUNNEL_HEADERS = {
    "Bypass-Tunnel-Reminder": "true",
    "ngrok-skip-browser-warning": "true",
    "User-Agent": "DataExpiry-App/1.0"
}

# --- Switchable View ---
st.caption("SWITCH VIEW")
active_view = st.radio(
    "View",
    ["👤 User View", "🕵️ Hacker View", "⚙️ Admin View", "📊 SOC Dashboard"],
    horizontal=True,
    label_visibility="collapsed",
    key="view_selector",
)

with st.container(border=True, key="view_panel"):
    if active_view == "👤 User View":
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
                res = requests.post(f"{PROXY_URL}/api/records", json=payload, headers=TUNNEL_HEADERS)
                if res.status_code in [200, 201]:
                    st.session_state["last_record_id"] = res.json().get("id")
                    st.session_state["expiry_time"] = time.time() + ttl
                    st.success(f"Data routed through Proxy with a {selected_ttl} retention policy!")
                else:
                    st.error(f"Proxy Error: {res.status_code} - {res.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to Proxy! (Check if port 8000 is running).")

    elif active_view == "🕵️ Hacker View":
        st.subheader("🕵️ Hacker View (Target Database)")
        st.info("Live peek inside `company_database.db`:")

        if st.button("Refresh Database View"):
            try:
                db_res = requests.get(f"{BACKEND_URL}/api/records", headers=TUNNEL_HEADERS)
                if db_res.status_code == 200:
                    records = db_res.json()
                    if records:
                        st.json(records)
                    else:
                        st.write("Database is currently empty.")
                else:
                    st.error(f"Failed to read database. Status Code: {db_res.status_code}")
            except requests.exceptions.ConnectionError:
                st.warning("Target backend (port 5000) is not running.")
                
    elif active_view == "📊 SOC Dashboard":
        st.subheader("📊 Security Operations Center (SIEM)")
        st.caption("Live immutable audit trail of all cryptographic proxy events.")
        
        soc_key = st.text_input("Admin API Key", type="password", key="soc_admin_key")
        
        if st.button("Fetch Live Telemetry"):
            try:
                headers = {"X-Admin-Key": soc_key, **TUNNEL_HEADERS}
                res = requests.get(f"{PROXY_URL}/api/admin/logs", headers=headers)
                
                if res.status_code == 200:
                    data = res.json()
                    summary = data.get("summary", {})
                    logs = data.get("logs", [])
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Active Encrypted Keys", summary.get("active_keys", 0))
                    col2.metric("Shredded Keys (Expired)", summary.get("shredded_keys", 0))
                    col3.metric("Decryption Attempts", summary.get("decryption_attempts", 0))
                    
                    st.divider()
                    st.write("### 📜 Immutable Event Ledger")
                    if logs:
                        st.dataframe(logs, use_container_width=True)
                    else:
                        st.info("No cryptographic events logged yet.")
                elif res.status_code == 401:
                    st.error("Invalid Admin Key!")
                else:
                    st.error(f"Error fetching logs: {res.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to Proxy.")

    else:
        st.subheader("⚙️ Enterprise DLP Config")
        st.caption("Configure which JSON fields the proxy encrypts on the fly.")

        admin_key = st.text_input("Admin API Key", type="password", key="admin_key_input")
        target_fields = st.text_input("Fields to Encrypt (comma-separated)", "sensitive_data", key="target_fields_input")

        if st.button("Apply Security Policies"):
            headers = {"X-Admin-Key": admin_key, **TUNNEL_HEADERS}
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
        if st.button("🔄 View Current Active Fields"):
            try:
                cfg_res = requests.get(f"{PROXY_URL}/api/admin/config", headers=TUNNEL_HEADERS)
                if cfg_res.status_code == 200:
                    st.info(f"Currently encrypting: {cfg_res.json().get('active_fields')}")
                else:
                    st.warning(f"Could not fetch config: {cfg_res.status_code}")
            except requests.exceptions.ConnectionError:
                st.warning("Proxy unreachable.")

# --- RESTORED: Live Expiry & Retrieval Demo (With thread-safe st.rerun loop) ---
if "expiry_time" in st.session_state and "last_record_id" in st.session_state:
    with st.container(border=True, key="expiry_panel"):
        st.subheader("⏱️ Live Expiry & Retrieval Test")

        timer_placeholder = st.empty()
        action_placeholder = st.empty()

        with action_placeholder.container():
            if st.button("Attempt Decrypted Read via Proxy"):
                rec_id = st.session_state["last_record_id"]
                try:
                    fetch_res = requests.get(f"{PROXY_URL}/api/records/{rec_id}", headers=TUNNEL_HEADERS)

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

        # Thread-Safe Live Countdown Loop
        remaining = int(st.session_state["expiry_time"] - time.time())

        if remaining > 0:
            if remaining <= 60: 
                timer_placeholder.warning(f"⏳ **LIVE COUNTDOWN:** `{remaining}s` remaining before cryptographic shredding...")
                time.sleep(1)
                st.rerun() 
            else:
                timer_placeholder.warning(f"⏳ **KEY ACTIVE:** `{remaining:,}s` remaining before cryptographic shredding...")
        else:
            timer_placeholder.error("🚨 **TTL EXPIRED:** Cryptographic key has been mathematically shredded in the Vault.")
