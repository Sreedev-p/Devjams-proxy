import streamlit as st
import requests
import time
import base64
from pathlib import Path

# --- Configuration ---
st.set_page_config(page_title="DataExpiry Demo", layout="wide")

# --- THEME DETECTION ---
# Streamlit already ships a native Light/Dark/System switcher (the "..." menu -> Settings).
# We read the currently active theme from it instead of adding a second, redundant toggle.
try:
    dark_mode = st.context.theme.type == "dark"
except Exception:
    # Older Streamlit versions without st.context.theme -> default to light styling
    dark_mode = False

# --- Color tokens for each theme, matching the light/dark pair in the reference site ---
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

# --- CUSTOM THEME (CSS INJECTION) - "TEAK-STYLE" REDESIGN, LIGHT + DARK ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Background with subtle dot grid, like the reference site (both themes) */
    [data-testid="stAppViewContainer"] {{
        background-color: {THEME["bg"]};
        background-image: radial-gradient(circle, {THEME["dot"]} 1px, transparent 1px);
        background-size: 22px 22px;
    }}

    [data-testid="stAppViewContainer"] > .main {{
        position: relative;
        z-index: 1;
    }}

    [data-testid="stHeader"] {{
        background-color: rgba(0, 0, 0, 0);
    }}

    /* Global font sizing */
    .stApp {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 16px !important;
        letter-spacing: -0.1px;
        color: {THEME["text"]} !important;
    }}

    .stApp h1 {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -1.4px;
        font-size: 2.75rem !important;
        margin-bottom: 1.5rem !important;
        color: {THEME["text"]} !important;
    }}

    .stApp h2 {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.9px;
        font-size: 1.75rem !important;
        margin-bottom: 1rem !important;
        color: {THEME["text"]} !important;
    }}

    .stApp h3 {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
        font-size: 1.25rem !important;
        color: {THEME["text"]} !important;
    }}

    /* Input fields */
    .stTextInput input {{
        font-size: 14px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        padding: 10px 12px !important;
        background-color: {THEME["surface"]} !important;
        border: 1px solid {THEME["border"]} !important;
        border-radius: 8px !important;
        color: {THEME["text"]} !important;
        box-shadow: {THEME["card_shadow"]};
        transition: border-color 0.15s ease;
    }}

    .stTextInput input:focus {{
        border-color: {THEME["accent"]} !important;
    }}

    .stSelectbox {{
        font-size: 14px !important;
    }}

    .stSelectbox > div > div {{
        background-color: {THEME["surface"]} !important;
        border: 1px solid {THEME["border"]} !important;
        border-radius: 8px !important;
        color: {THEME["text"]} !important;
    }}

    /* Buttons - yellow pill, like the reference "Book a demo" button */
    .stButton button {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.2px;
        font-size: 14px !important;
        padding: 10px 20px !important;
        background-color: {THEME["accent"]} !important;
        color: {THEME["accent_text"]} !important;
        border: none !important;
        border-radius: 999px !important;
        box-shadow: {THEME["button_shadow"]};
        transition: transform 0.15s ease, background-color 0.15s ease, box-shadow 0.15s ease;
    }}

    .stButton button:hover {{
        background-color: {THEME["accent_hover"]} !important;
        color: {THEME["accent_text"]} !important;
        box-shadow: {THEME["button_shadow_hover"]};
        transform: translateY(-1px);
    }}

    .stButton button:active {{
        background-color: {THEME["accent_active"]} !important;
    }}

    /* Alerts & Messages */
    div[data-testid="stAlert"] {{
        background-color: {THEME["surface"]};
        border: 1px solid {THEME["border"]};
        border-radius: 10px;
        padding: 16px !important;
        font-size: 14px !important;
        color: {THEME["text"]} !important;
        box-shadow: {THEME["card_shadow"]};
    }}

    /* Sidebar specific */
    [data-testid="stSidebar"] {{
        background-color: {THEME["sidebar_bg"]};
        border-right: 1px solid {THEME["border"]};
    }}

    [data-testid="stSidebar"] .stTextInput input {{
        font-size: 13px !important;
    }}

    [data-testid="stSidebar"] .stMarkdownContainer {{
        font-size: 14px !important;
        color: {THEME["text"]} !important;
    }}

    [data-testid="stSidebar"] h2 {{
        font-size: 1.5rem !important;
    }}

    /* Divider */
    hr {{
        margin: 2rem 0 !important;
        border-color: {THEME["border"]} !important;
    }}

    /* JSON display - monospace, matches the technical look of the reference site */
    .stJson {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
        background-color: {THEME["surface_alt"]} !important;
        border: 1px solid {THEME["border"]} !important;
        border-radius: 8px !important;
        box-shadow: {THEME["card_shadow"]};
    }}

    /* Cards for columns (subheaders act as section headers) */
    .stColumn {{
        background-color: transparent;
    }}

    /* Captions - monospace, mirrors the small stat labels ("30%+ Higher CTR") in the reference */
    .stCaption, [data-testid="stCaptionContainer"] {{
        font-family: 'JetBrains Mono', monospace !important;
        color: {THEME["muted"]} !important;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        font-size: 12px !important;
    }}

    /* ===== View switcher: turn st.radio into a premium pill toggle, ===== */
    /* ===== not the default Streamlit radio look.                    ===== */
    .st-key-view_selector div[role="radiogroup"] {{
        display: inline-flex;
        gap: 4px;
        background-color: {THEME["surface_alt"]};
        border: 1px solid {THEME["border"]};
        border-radius: 999px;
        padding: 4px;
    }}

    .st-key-view_selector label {{
        margin: 0 !important;
        cursor: pointer;
    }}

    /* Hide the default circular radio indicator */
    .st-key-view_selector label > div:first-child {{
        display: none !important;
    }}

    /* Style the option text as a pill button */
    .st-key-view_selector label > div:last-child {{
        padding: 10px 22px !important;
        border-radius: 999px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        color: {THEME["muted"]} !important;
        white-space: nowrap;
        transition: background-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
    }}

    .st-key-view_selector label:hover > div:last-child {{
        color: {THEME["text"]} !important;
    }}

    /* Selected pill - highlighted in the same accent as the primary buttons */
    .st-key-view_selector label:has(input:checked) > div:last-child {{
        background-color: {THEME["accent"]} !important;
        color: {THEME["accent_text"]} !important;
        box-shadow: {THEME["button_shadow"]};
    }}

    /* ===== Card panels wrapping each view / the expiry test ===== */
    .st-key-view_panel,
    .st-key-expiry_panel {{
        border-radius: 18px !important;
    }}

    .st-key-view_panel > div[data-testid="stVerticalBlockBorderWrapper"],
    .st-key-expiry_panel > div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {THEME["surface"]} !important;
        border: 1px solid {THEME["border"]} !important;
        border-radius: 18px !important;
        box-shadow: {THEME["card_shadow"]};
        padding: 1.75rem !important;
    }}

    .st-key-expiry_panel {{
        margin-top: 1.5rem;
    }}
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
    if st.button("View Current Active Fields"):
        try:
            cfg_res = requests.get(f"{PROXY_URL}/api/admin/config")
            if cfg_res.status_code == 200:
                st.info(f"Currently encrypting: {cfg_res.json().get('active_fields')}")
            else:
                st.warning(f"Could not fetch config: {cfg_res.status_code}")
        except requests.exceptions.ConnectionError:
            st.warning("Proxy unreachable.")

# --- Switchable View: User View vs Hacker View ---
st.caption("SWITCH VIEW")
active_view = st.radio(
    "View",
    ["User View", "Hacker View"],
    horizontal=True,
    label_visibility="collapsed",
    key="view_selector",
)

with st.container(border=True, key="view_panel"):
    if active_view == "User View":
        st.subheader("Client / Application View")
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

    else:
        st.subheader("Hacker View (Target Database)")
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

# --- Live Expiry & Retrieval Demo ---
if "expiry_time" in st.session_state and "last_record_id" in st.session_state:
    with st.container(border=True, key="expiry_panel"):
        st.subheader("Live Expiry & Retrieval Test")

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
