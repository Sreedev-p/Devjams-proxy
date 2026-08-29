import streamlit as st
import requests
import time

st.set_page_config(page_title="DataExpiry Demo", layout="wide")
st.title("🛡️ DataExpiry: Zero-Code Cryptographic Erasure")

# dashboard/app.py (around line 8)
PROXY_URL = "https://c361391c250129.lhr.life"
BACKEND_URL = "https://6e63d2d51e6eac.lhr.life"

col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Client / Application View")
    user_name = st.text_input("Customer Name", "Alice Smith")
    sensitive_data = st.text_input("Sensitive Data (e.g. Card / SSN)", "4532-xxxx-xxxx-8891")
    ttl = st.slider("Time-To-Live (Seconds)", min_value=5, max_value=60, value=10)
    
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
                st.success("Data securely routed through Proxy!")
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
    
    # Allows judges to see the time updating without refreshing the whole page
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
