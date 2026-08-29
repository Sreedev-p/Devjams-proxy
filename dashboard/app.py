import streamlit as st
import requests
import time
import base64
from pathlib import Path

# --- Configuration ---
st.set_page_config(page_title="DataExpiry Demo", layout="wide")

PROXY_URL = "https://6e3319dd2e30ff.lhr.life"
BACKEND_URL = "https://bd2dfb593379b0.lhr.life"
BG_IMAGE_PATH = "cyber-background-8k.png"
REQUEST_TIMEOUT = 10

# --- Session state ---
st.session_state.setdefault("last_record_id", None)
st.session_state.setdefault("expiry_time", None)

# --- BACKGROUND IMAGE (base64 embed so it works local or deployed) ---
@st.cache_data
def get_base64_image(image_path):
    path = Path(image_path)
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_base64 = get_base64_image(BG_IMAGE_PATH)

if bg_base64:
    bg_css = '''
        background-image: url("data:image/png;base64,''' + bg_base64 + '''");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    '''
else:
    bg_css = "background-color: #050505;"

# --- CUSTOM THEME (CSS INJECTION) ---
custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

    [data-testid="stAppViewContainer"] {
        """ + bg_css + """
    }

    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(5, 5, 5, 0.95);
        z-index: 0;
        pointer-events: none;
    }

    [data-testid="stAppViewContainer"] > .main {
        position: relative;
        z-index: 1;
    }

    [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0);
    }

    .stApp, p, span, label, div {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 15px !important;
        letter-spacing: -0.1px;
    }

    .stApp h1 {
        font-family: 'Playfair Display', serif !important;
        font-weight: 500 !important;
        color: #ffffff !important;
        letter-spacing: -0.5px;
        font-size: 2.8rem !important;
        margin-bottom: 1.5rem !important;
    }

    .stApp h2 {
        font-family: 'Playfair Display', serif !important;
        font-weight: 500 !important;
        color: #ffffff !important;
        letter-spacing: -0.5px;
        font-size: 1.75rem !important;
        margin-bottom: 1rem !important;
    }

    .stApp h3 {
        font-family: 'Playfair Display', serif !important;
        font-weight: 500 !important;
        color: #ffffff !important;
        letter-spacing: -0.5px;
        font-size: 1.25rem !important;
    }

    .stTextInput input {
        background-color: #0a0a0a !important;
        border: 1px solid #2a2a2a !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        font-family: 'Inter', sans-serif !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
    }

    .stSelectbox div[data-baseweb="select"] {
        background-color: #0a0a0a !important;
        border: 1px solid #2a2a2a !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
    }

    .stButton button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 50px !important;
        border: none !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        padding: 10px 24px !important;
    }

    .stButton button:hover {
        background-color: #e0e0e0 !important;
    }

    div[data-testid="stAlert"] {
        background-color: #0a0a0a !important;
        border: 1px solid #222222 !important;
        border-radius: 6px !important;
        color: #d1d1d1 !important;
        padding: 16px !important;
        font-size: 14px !important;
    }

    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid #1a1a1a !important;
    }

    .stJson {
        font-size: 13px !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 1px solid #222222 !important;
        gap: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif !important;
        color: #777777 !important;
        font-weight: 400 !important;
        padding-bottom: 12px !important;
        border-bottom: 2px solid transparent !important;
    }

    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        border-bottom: 2px solid #ffffff !important;
        font-weight: 500 !important;
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.title("🛡️ DataExpiry: Zero-Code Cryptographic Erasure")

# Tunnel bypass headers
TUNNEL_HEADERS = {
    "Bypass-Tunnel-Reminder": "true",
    "ngrok-skip-browser-warning": "true",
    "User-Agent": "DataExpiry-App/1.0"
}

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("⚙️ Enterprise DLP Config")

    st.caption(
        "Configure which JSON fields the proxy encrypts on the fly. "
        "Changes are saved permanently in the SQLite vault and apply immediately."
    )

    admin_key = st.text_input("Admin API Key", type="password", key="admin_key_input")
    target_fields = st.text_input(
        "Fields to Encrypt (comma-separated)",
        "sensitive_data",
        key="target_fields_input"
    )

    if st.button("Apply Security Policies"):
        headers = {"X-Admin-Key": admin_key, **TUNNEL_HEADERS}
        payload = {"fields": target_fields}
        try:
            res = requests.post(
                f"{PROXY_URL}/api/admin/config",
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            if res.status_code in [200, 201]:
                st.success(f"Active fields: {res.json().get('active_fields')}")
            elif res.status_code == 401:
                st.error("Invalid Admin Key!")
            else:
                st.error(f"Unexpected error: {res.status_code} - {res.text}")
        except requests.exceptions.Timeout:
            st.error("Proxy request timed out.")
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach proxy.")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

    st.divider()

    if st.button("🔄 View Current Active Fields"):
        try:
            cfg_res = requests.get(
                f"{PROXY_URL}/api/admin/config",
                headers=TUNNEL_HEADERS,
                timeout=REQUEST_TIMEOUT
            )
            if cfg_res.status_code == 200:
                st.info(f"Currently encrypting: {cfg_res.json().get('active_fields')}")
            else:
                st.warning(f"Could not fetch config: {cfg_res.status_code}")
        except requests.exceptions.Timeout:
            st.warning("Proxy request timed out.")
        except requests.exceptions.ConnectionError:
            st.warning("Proxy unreachable.")
        except requests.exceptions.RequestException as e:
            st.warning(f"Request failed: {e}")

# =========================================================
# MAIN UI
# =========================================================
tab1, tab2 = st.tabs(["👤 Client / Application View", "🕵️ Hacker View (Target Database)"])

with tab1:
    st.subheader("Client Details")
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

    selected_ttl = st.selectbox(
        "Data Retention Policy (Time-To-Live)",
        list(ttl_options.keys())
    )
    ttl = ttl_options[selected_ttl]

    if st.button("Submit Sensitive Data"):
        payload = {
            "user_name": user_name,
            "sensitive_data": sensitive_data,
            "ttl_seconds": ttl
        }
        try:
            res = requests.post(
                f"{PROXY_URL}/api/records",
                json=payload,
                headers=TUNNEL_HEADERS,
                timeout=REQUEST_TIMEOUT
            )
            if res.status_code in [200, 201]:
                body = res.json()
                st.session_state["last_record_id"] = body.get("id")
                st.session_state["expiry_time"] = time.time() + ttl
                st.success(f"Data routed through Proxy with a {selected_ttl} retention policy!")
            else:
                st.error(f"Proxy Error: {res.status_code} - {res.text}")
        except requests.exceptions.Timeout:
            st.error("Proxy request timed out.")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to Proxy.")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

with tab2:
    st.subheader("Target Database Contents")
    st.info("Live peek inside `company_database.db`:")

    if st.button("Refresh Database View"):
        try:
            db_res = requests.get(
                f"{BACKEND_URL}/api/records",
                headers=TUNNEL_HEADERS,
                timeout=REQUEST_TIMEOUT
            )
            if db_res.status_code == 200:
                records = db_res.json()
                if records:
                    st.json(records)
                else:
                    st.write("Database is currently empty.")
            else:
                st.error(f"Failed to read database: {db_res.status_code}")
        except requests.exceptions.Timeout:
            st.warning("Target backend request timed out.")
        except requests.exceptions.ConnectionError:
            st.warning("Target backend is not reachable.")
        except requests.exceptions.RequestException as e:
            st.warning(f"Request failed: {e}")

st.divider()

# =========================================================
# LIVE EXPIRY & RETRIEVAL DEMO
# =========================================================
if st.session_state.get("expiry_time") and st.session_state.get("last_record_id"):
    st.subheader("⏱️ Live Expiry & Retrieval Test")

    rec_id = st.session_state["last_record_id"]

    if st.button("Attempt Decrypted Read via Proxy"):
        try:
            fetch_res = requests.get(
                f"{PROXY_URL}/api/records/{rec_id}",
                headers=TUNNEL_HEADERS,
                timeout=REQUEST_TIMEOUT
            )

            if fetch_res.status_code == 200:
                st.success("200 OK: Key active. Decrypted plaintext restored.")
                st.json(fetch_res.json())
            elif fetch_res.status_code == 410:
                st.error("410 Gone: Decryption key permanently erased from Vault.")
                try:
                    st.json(fetch_res.json())
                except Exception:
                    st.code(fetch_res.text)
            else:
                st.warning(f"Unexpected Proxy response: {fetch_res.status_code}")
                try:
                    st.json(fetch_res.json())
                except Exception:
                    st.code(fetch_res.text)

        except requests.exceptions.Timeout:
            st.error("Proxy retrieval request timed out.")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to Proxy for retrieval.")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

    remaining = max(0, int(st.session_state["expiry_time"] - time.time()))

    if remaining > 0:
        if remaining <= 60:
            st.warning(
                f"⏳ **LIVE COUNTDOWN:** `{remaining}s` remaining before cryptographic shredding..."
            )
        else:
            st.warning(
                f"⏳ **KEY ACTIVE:** `{remaining:,}s` remaining before cryptographic shredding..."
            )
    else:
        st.error("🚨 **TTL EXPIRED:** Cryptographic key has been mathematically shredded in the Vault.")
