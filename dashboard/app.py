import streamlit as st
import requests
import time

# --- Configuration ---
st.set_page_config(page_title="DataExpiry Demo", layout="wide")

# --- CUSTOM THEME (CSS INJECTION) ---
st.markdown("""
    <style>
    /* Force background to pure black */
    [data-testid="stAppViewContainer"] {
        background-color: #000000;
    }
    /* Make the top header transparent so it doesn't clash */
    [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0);
    }
    /* Apply a clean, professional enterprise font to all elements */
    * {
        font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    }
    /* Slightly darken the alert boxes so they look good on pure black */
    div[data-testid="stAlert"] {
        background-color: #111111;
        border: 1px solid #333333;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ DataExpiry: Zero-Code Cryptographic Erasure")

PROXY_URL = "http://127.0.0.1:8000"
BACKEND_URL = "http://127.0.0.1:5000" 

# --- Main Split-Screen UI ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Client / Application View")
    user_name = st.text_input("Customer Name", "Alice Smith")
    sensitive_data = st.text_input("Sensitive Data (e.g. Card / SSN)", "4532-xxxx-xxxx-8891")
    
    # Dropdown for professional retention policies
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
            if res.status_code == 201:
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
