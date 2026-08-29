import streamlit as st
import requests
import time

# --- Configuration ---
st.set_page_config(page_title="DataExpiry Demo", layout="wide")
st.title("🛡️ DataExpiry: Zero-Code Cryptographic Erasure")

# The URL of your teammate's proxy (you will update this IP later when linking machines)
PROXY_URL = "http://127.0.0.1:8000"

# --- Main Split-Screen UI ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Client / Application View")
    user_name = st.text_input("Customer Name", "Alice Smith")
    sensitive_data = st.text_input("Sensitive Payload (e.g. Card / SSN)", "4532-xxxx-xxxx-8891")
    ttl = st.slider("Time-To-Live (Seconds)", min_value=5, max_value=60, value=10)
    
    if st.button("Submit Sensitive Data"):
        payload = {
            "user_name": user_name,
            "sensitive_payload": sensitive_data,
            "ttl_seconds": ttl
        }
        try:
            # Forwarding data to the Proxy Interceptor
            res = requests.post(f"{PROXY_URL}/records", json=payload)
            if res.status_code == 200:
                st.session_state["last_response"] = res.json()
                st.session_state["expiry_time"] = time.time() + ttl
                st.success("Data securely routed through Proxy!")
            else:
                st.error(f"Proxy Error: {res.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to Proxy! (Wait for your Linux teammate to start it).")

with col2:
    st.subheader("🕵️ Target Database / Hacker View")
    if "last_response" in st.session_state:
        st.info("What is sitting in the vulnerable company database (Ciphertext only):")
        st.json(st.session_state["last_response"])

st.divider()

# --- Live Expiry & Retrieval Demo ---
if "expiry_time" in st.session_state:
    st.subheader("⏱️ Live Expiry & Retrieval Test")
    
    # Calculate time remaining
    remaining = int(st.session_state["expiry_time"] - time.time())
    
    if remaining > 0:
        st.warning(f"Key TTL active: {remaining}s remaining before shredding...")
    else:
        st.error("TTL expired! Cryptographic key has been mathematically shredded.")
        
    if st.button("Attempt Decrypted Read via Proxy"):
        rec_id = st.session_state["last_response"].get("data_id")
        try:
            fetch_res = requests.get(f"{PROXY_URL}/records/{rec_id}")
            
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
