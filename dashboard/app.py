import streamlit as st
import requests
import time
import base64
from pathlib import Path

# --- Configuration ---
st.set_page_config(page_title="DataExpiry Demo", layout="wide")

# --- BACKGROUND IMAGE (base64 embed so it works local or deployed) ---
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

# --- CUSTOM THEME (CSS INJECTION) - FIXED ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Manrope:wght@400;500;600;700&display=swap');

    [data-testid="stAppViewContainer"] {{
        {bg_css}
    }}

    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
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

    /* Global font sizing - reasonable defaults */
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

    /* Input fields */
    .stTextInput input {{
        font-size: 14px !important;
        font-family: 'Manrope', sans-serif !important;
        padding: 10px 12px !important;
    }}

    .stSelectbox {{
        font-size: 14px !important;
    }}

    /* Buttons */
    .stButton button {{
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.2px;
        font-size: 14px !important;
        padding: 10px 20px !important;
    }}

    /* Alerts & Messages */
    div[data-testid="stAlert"] {{
        background-color: rgba(17, 17, 17, 0.85);
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 16px !important;
        font-size: 14px !important;
    }}

    /* Sidebar specific */
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

    /* Divider */
    hr {{
        margin: 2rem 0 !important;
    }}

    /* JSON display */
    .stJson {{
        font-size: 13px !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ DataExpiry: Zero-Code Cryptographic Erasure")

PROXY_URL = "https://6e3319dd2e30ff.lhr.life"
BACKEND_URL = "https://bd2dfb593379b0.lhr.life"

# BYPASS HEADERS to prevent Localtunnel HTML warning screens from crashing the JSON parser
TUNNEL_HEADERS = {
    "Bypass-Tunnel-Reminder": "true",
    "ngrok-skip-browser-warning": "true",
    "User-Agent": "DataExpiry-App/1.0"
}

# =========================================================
# SIDEBAR: Enterprise DLP Admin Config Panel
# =========================================================
with st.sidebar:
    st.header("⚙️ Enterprise DLP Config")

    st.caption("Configure which JSON fields the proxy encrypts on the fly. Changes are saved permanently in the SQLite vault and apply immediately, no restart needed.")

    admin_key = st.text_input("Admin API Key", type="password", key="admin_key_input")
    target_fields = st.text_input("Fields to Encrypt (comma-separated)", "sensitive_data", key="target_fields_input")

    if st.button("Apply Security Policies"):
        # Merges the admin key with the tunnel bypass headers
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
            res = requests.post(f"{PROXY_URL}/api/records", json=payload, headers=TUNNEL_HEADERS)
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
            db_res = requests.get(f"{BACKEND_URL}/api/records", headers=TUNNEL_HEADERS)
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

    # 1. Create the placeholder FIRST so it renders above the buttons
    timer_placeholder = st.empty()

    # 2. Render the Action Button (visible and clickable while timer runs)
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

    # 3. Execute the Live Countdown Loop at the absolute bottom of the script
    remaining = int(st.session_state["expiry_time"] - time.time())

    # --- Live Expiry & Retrieval Demo ---
    if "expiry_time" in st.session_state and "last_record_id" in st.session_state:
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

        # 3. Thread-Safe Live Countdown Loop
        remaining = int(st.session_state["expiry_time"] - time.time())

        if remaining > 0:
            if remaining <= 60: 
                timer_placeholder.warning(f"⏳ **LIVE COUNTDOWN:** `{remaining}s` remaining before cryptographic shredding...")
                time.sleep(1)
                st.rerun() # Safely restarts the script from the top to update the UI
            else:
                timer_placeholder.warning(f"⏳ **KEY ACTIVE:** `{remaining:,}s` remaining before cryptographic shredding...")
        else:
            timer_placeholder.error("🚨 **TTL EXPIRED:** Cryptographic key has been mathematically shredded in the Vault.")
