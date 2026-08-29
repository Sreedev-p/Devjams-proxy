import streamlit as st
import requests
import time

# --- Configuration ---
st.set_page_config(page_title="DataExpiry Demo", layout="wide")

# --- PREMIUM SAAS THEME (CSS INJECTION) ---
st.markdown("""
    <style>
    /* Import Premium Fonts: Playfair Display for elegant headers, Inter for clean UI text */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

    /* Global Base - Pure Black */
    [data-testid="stAppViewContainer"] {
        background-color: #000000;
        color: #e5e5e5;
    }
    
    [data-testid="stHeader"] {
        background-color: transparent;
    }

    /* Sidebar - Very dark charcoal to separate slightly from main body */
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #1a1a1a;
    }

    /* Typography - Body */
    .stApp, p, span, label, div {
        font-family: 'Inter', sans-serif !important;
        font-size: 15px !important;
        letter-spacing: -0.1px;
    }

    /* Typography - Headings (The Editorial Serif Look) */
    h1, h2, h3, h4 {
        font-family: 'Playfair Display', serif !important;
        font-weight: 500 !important;
        color: #ffffff !important;
        letter-spacing: -0.5px;
    }
    
    h1 {
        font-size: 3.5rem !important;
        margin-bottom: 1rem !important;
        line-height: 1.1 !important;
    }

    h2 {
        font-size: 2rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Inputs & Select Boxes - Dark, minimal borders */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0a0a0a !important;
        border: 1px solid #2a2a2a !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        font-family: 'Inter', sans-serif !important;
        padding: 12px 16px !important;
        transition: border-color 0.2s ease;
    }
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus {
        border-color: #ffffff !important;
    }

    /* Buttons - Premium White Pill Style (from reference image) */
    .stButton button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 50px !important; /* Pill shape */
        border: none !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease !important;
    }
    .stButton button:hover {
        background-color: #e0e0e0 !important;
        transform: translateY(-1px);
    }

    /* Alerts & Messages - Stripped of harsh colors, made minimalist */
    div[data-testid="stAlert"] {
        background-color: #0a0a0a !important;
        border: 1px solid #222222 !important;
        border-radius: 6px !important;
        color: #d1d1d1 !important;
        padding: 16px !important;
    }

    /* Tab Styling - Clean underlines */
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
    
    /* Dividers */
    hr {
        border-color: #222222 !important;
        margin: 3rem 0 !important;
    }
    </style>
""", unsafe_allow_html=True)


st.title("DataExpiry.")
st.markdown("<p style='color: #888; font-size: 1.1rem; margin-top: -20px; margin-bottom: 30px;'>Zero-Code Cryptographic Erasure for Enterprise.</p>", unsafe_allow_html=True)

PROXY_URL = "https://6e3319dd2e30ff.lhr.life"
BACKEND_URL = "https://bd2dfb593379b0.lhr.life"

# BYPASS HEADERS to prevent Localtunnel HTML warning screens
TUNNEL_HEADERS = {
    "Bypass-Tunnel-Reminder": "true",
    "ngrok-skip-browser-warning": "true",
    "User-Agent": "DataExpiry-App/1.0"
}

# =========================================================
# SIDEBAR: Enterprise DLP Admin Config Panel
# =========================================================
with st.sidebar:
    st.header("Admin Config")

    st.caption("Configure dynamic JSON field encryption. Changes sync to SQLite and apply immediately.")

    admin_key = st.text_input("Admin API Key", type="password", key="admin_key_input")
    target_fields = st.text_input("Fields to Encrypt (comma-separated)", "sensitive_data", key="target_fields_input")

    if st.button("Apply Policies"):
        headers = {"X-Admin-Key": admin_key, **TUNNEL_HEADERS}
        payload = {"fields": target_fields}
        try:
            res = requests.post(f"{PROXY_URL}/api/admin/config", json=payload, headers=headers)
            if res.status_code in [200, 201]:
                st.success(f"Active fields: {res.json().get('active_fields')}")
            elif res.status_code == 401:
                st.error("Invalid Admin Key.")
            else:
                st.error(f"Unexpected error: {res.status_code} - {res.text}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach proxy.")

    st.divider()

    if st.button("View Active Fields"):
        try:
            cfg_res = requests.get(f"{PROXY_URL}/api/admin/config", headers=TUNNEL_HEADERS)
            if cfg_res.status_code == 200:
                st.info(f"Currently encrypting: {cfg_res.json().get('active_fields')}")
            else:
                st.warning(f"Could not fetch config: {cfg_res.status_code}")
        except requests.exceptions.ConnectionError:
            st.warning("Proxy unreachable.")

# =========================================================
# MAIN UI: Tabbed Views
# =========================================================
tab1, tab2 = st.tabs(["Client Environment", "Target Database"])

with tab1:
    st.subheader("Simulate Data Flow")
    user_name = st.text_input("Customer Name", "Alice Smith")
    sensitive_data = st.text_input("Sensitive Payload", "4532-xxxx-xxxx-8891")

    ttl_options = {
        "15 Seconds (Live Pitch Demo)": 15,
        "30 Seconds (Standard Demo)": 30,
        "1 Hour (Temporary Cache)": 3600,
        "24 Hours (Daily Rotation)": 86400,
        "30 Days (Standard Compliance)": 2592000,
        "1 Year (Enterprise Archival)": 31536000
    }
    selected_ttl = st.selectbox("Data Retention Policy", list(ttl_options.keys()))
    ttl = ttl_options[selected_ttl]

    if st.button("Submit to Proxy"):
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
                st.success(f"Secured with {selected_ttl} retention.")
            else:
                st.error(f"Proxy Error: {res.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to Proxy.")

with tab2:
    st.subheader("Database Ciphertext")
    st.info("Live interception of company_database.db:")

    if st.button("Refresh View"):
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
            st.warning("Target backend is not running.")

st.divider()

# --- Live Expiry & Retrieval Demo ---
if "expiry_time" in st.session_state and "last_record_id" in st.session_state:
    st.subheader("Cryptographic Validation")

    timer_placeholder = st.empty()

    if st.button("Attempt Decrypted Read"):
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

    # Live Countdown Loop
    remaining = int(st.session_state["expiry_time"] - time.time())

    if remaining > 0:
        if remaining <= 60: 
            while remaining > 0:
                timer_placeholder.info(f"⏳ TTL Active: {remaining}s remaining before key shredding.")
                time.sleep(1)
                remaining = int(st.session_state["expiry_time"] - time.time())
            
            timer_placeholder.error("🚨 TTL Expired: Key mathematically shredded.")
        else:
            timer_placeholder.info(f"⏳ TTL Active: {remaining:,}s remaining before key shredding.")
    else:
        timer_placeholder.error("🚨 TTL Expired: Key mathematically shredded.")
