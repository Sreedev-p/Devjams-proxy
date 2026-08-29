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
        bg": "#0B1020",
    "dot": "rgba(148, 163, 184, 0.08)",
    "text": "#E6EEF8",
    "muted": "#94A3B8",
    "surface": "#121A2B",
    "surface_alt": "#182338",
    "border": "rgba(148, 163, 184, 0.20)",
    "sidebar_bg": "#0F172A",
    "accent": "#22D3EE",
    "accent_hover": "#06B6D4",
    "accent_active": "#67E8F9",
    "accent_text": "#06131A",
    "accent_active_text": "#06131A",
    "danger": "#F87171",
    "danger_text": "#200A0A",
    "success": "#34D399",
    "warning": "#FBBF24",
    "button_shadow": "0 0 0 1px rgba(34, 211, 238, 0.18), 0 10px 24px rgba(8, 15, 30, 0.35)",
    "button_shadow_hover": "0 0 0 1px rgba(34, 211, 238, 0.28), 0 14px 30px rgba(8, 15, 30, 0.45)",
    "card_shadow": "0 8px 28px rgba(2, 6, 23, 0.36)",
    }
else:
    THEME = {
        "bg": "#A3B18A",
        "dot": "rgba(52, 78, 65, 0.12)",
        "text": "#344E41",
        "muted": "#3A5A40",
        "surface": "#DAD7CD",
        "surface_alt": "#EDE9D8",
        "border": "rgba(58, 90, 64, 0.35)",
        "sidebar_bg": "#DAD7CD",
        "accent": "#588157",
        "accent_hover": "#3A5A40",
        "accent_active": "#344E41",
        "accent_text": "#DAD7CD",
        "accent_active_text": "#DAD7CD",
        "danger": "#344E41",
        "danger_text": "#DAD7CD",
        "button_shadow": "0 1px 2px rgba(52, 78, 65, 0.18)",
        "button_shadow_hover": "0 4px 14px rgba(58, 90, 64, 0.35)",
        "card_shadow": "0 2px 6px rgba(52, 78, 65, 0.18)",
    }

# --- CUSTOM THEME (CSS INJECTION) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root, .stApp {{
        --primary-color: {THEME["accent"]} !important;
    }}

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

    .stTextInput input:focus {{
        border-color: {THEME["accent"]} !important;
        box-shadow: 0 0 0 1px {THEME["accent"]} !important;
        outline: none !important;
    }}

    .stTextInput input:focus-visible {{
        box-shadow: 0 0 0 1px {THEME["accent"]} !important;
        outline: none !important;
    }}

    /* Streamlit renders inputs inside a BaseWeb wrapper div that draws its
       own focus ring independently of the <input> element above — this is
       the actual source of the red outline on password/text fields, so it
       needs to be overridden directly rather than relying on the input's
       own :focus styles alone. */
    div[data-baseweb="input"],
    div[data-baseweb="base-input"] {{
        border-color: {THEME["border"]} !important;
    }}

    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="base-input"]:focus-within {{
        border-color: {THEME["accent"]} !important;
        box-shadow: 0 0 0 1px {THEME["accent"]} !important;
    }}

    input:focus, input:focus-visible {{
        outline: none !important;
        box-shadow: none !important;
    }}

    .stSelectbox > div > div {{
        background-color: {THEME["surface"]} !important;
        border: 1px solid {THEME["border"]} !important;
        border-radius: 8px !important;
        color: {THEME["text"]} !important;
    }}

    .stSelectbox > div > div:focus-within {{
        border-color: {THEME["accent"]} !important;
        box-shadow: 0 0 0 1px {THEME["accent"]} !important;
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

    .stButton button:active {{
        background-color: {THEME["accent_active"]} !important;
        color: {THEME["accent_active_text"]} !important;
        transform: translateY(0px);
    }}

    div[data-testid="stAlert"] {{
        background-color: {THEME["surface"]};
        border: 1px solid {THEME["border"]};
        border-radius: 10px;
        color: {THEME["text"]} !important;
        box-shadow: {THEME["card_shadow"]};
    }}

    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span,
    div[data-testid="stAlert"] div,
    div[data-testid="stAlert"] a {{
        color: {THEME["text"]} !important;
    }}

    div[data-testid="stAlert"] code {{
        color: {THEME["muted"]} !important;
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
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

    /* Streamlit's radio "dot" isn't a native <input> we can theme with
       accent-color — it's custom-drawn (SVG or a styled div) using
       Streamlit's own default primary color (#FF4B4B), often applied via
       an inline style. Overriding every plausible paint property here,
       with !important, so it can't be beaten by that inline style. */
    .st-key-view_selector [data-testid="stRadio"] svg,
    .st-key-view_selector [data-testid="stRadio"] svg circle,
    .st-key-view_selector [data-testid="stRadio"] svg path {{
        fill: {THEME["accent"]} !important;
        stroke: {THEME["accent"]} !important;
    }}

    .st-key-view_selector [data-baseweb="radio"] div {{
        background-color: transparent;
        border-color: {THEME["accent"]} !important;
    }}

    .st-key-view_selector [data-baseweb="radio"] div[aria-checked="true"],
    .st-key-view_selector [data-baseweb="radio"] div:has(input:checked) {{
        background-color: {THEME["accent"]} !important;
        border-color: {THEME["accent"]} !important;
    }}

    .st-key-view_selector input[type="radio"] {{
        accent-color: {THEME["accent"]} !important;
    }}

    /* Belt-and-suspenders: force Streamlit's own theme variable to the
       accent color, scoped to just this widget, in case the dot color is
       actually being read from --primary-color rather than hardcoded. */
    .st-key-view_selector [data-testid="stRadio"] {{
        --primary-color: {THEME["accent"]} !important;
    }}

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

    /* "+" add-field button — ghost/dashed style so it reads as a small
       inline control rather than a full primary action button. */
    .st-key-add_field_btn button {{
        background-color: transparent !important;
        color: {THEME["accent"]} !important;
        border: 1px dashed {THEME["border"]} !important;
        box-shadow: none !important;
        width: auto;
        padding-left: 24px !important;
        padding-right: 24px !important;
    }}

    .st-key-add_field_btn button:hover {{
        border-color: {THEME["accent"]} !important;
        background-color: {THEME["surface_alt"]} !important;
    }}

    /* Field-remove "✕" buttons are destructive actions, so they get their
       own red treatment distinct from the primary accent color used on
       every other button — a deliberate, purposeful use of the palette's
       red swatch rather than leaving it unused. */
    div[class*="st-key-remove_field_"] button {{
        background-color: transparent !important;
        color: {THEME["danger"]} !important;
        border: 1px solid {THEME["danger"]} !important;
        box-shadow: none !important;
    }}

    div[class*="st-key-remove_field_"] button:hover {{
        background-color: {THEME["danger"]} !important;
        color: {THEME["danger_text"]} !important;
        box-shadow: none !important;
        transform: none !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("DataExpiry: Zero-Code Cryptographic Erasure")
PROXY_URL = "https://latrine-primal-retired.ngrok-free.dev"
BACKEND_URL = "https://thirty-plants-boil.loca.lt"

# RESTORED BYPASS HEADERS
TUNNEL_HEADERS = {
    "Bypass-Tunnel-Reminder": "true",
    "ngrok-skip-browser-warning": "true",
    "User-Agent": "DataExpiry-App/1.0"
}

# --- Switchable View ---
st.caption("")
active_view = st.radio(
    "View",
    ["User View", "Hacker View", "Admin View", "SOC Dashboard"],
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
                res = requests.post(f"{PROXY_URL}/api/records", json=payload, headers=TUNNEL_HEADERS)
                if res.status_code in [200, 201]:
                    st.session_state["last_record_id"] = res.json().get("id")
                    st.session_state["expiry_time"] = time.time() + ttl
                    st.success(f"Data routed through Proxy with a {selected_ttl} retention policy!")
                else:
                    st.error(f"Proxy Error: {res.status_code} - {res.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to Proxy! (Check if port 8000 is running).")

    elif active_view == "Hacker View":
        st.subheader("Hacker View (Target Database)")
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

    elif active_view == "SOC Dashboard":
        st.subheader("Security Operations Center (SIEM)")
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
                    st.write("### Immutable Event Ledger")
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
        st.subheader("Enterprise DLP Config")
        st.caption("Configure which JSON fields the proxy encrypts on the fly.")

        # Admin key box no longer stretches the full panel width — a
        # password/key field doesn't need that much horizontal space.
        key_col, _spacer = st.columns([1, 1])
        with key_col:
            admin_key = st.text_input("Admin API Key", type="password", key="admin_key_input")

        # --- Dynamic "Fields to Encrypt" list, replaces the old single ---
        # --- comma-separated text input with a proper +/- add/remove UI. ---
        # Fields are packed two-per-row so the leftover horizontal space is
        # used for the next field instead of sitting empty. If a row ends
        # up with only one field (an odd field out), the "＋ Add Field"
        # control is placed in that row's free slot instead of on its own
        # near-empty row below.
        st.caption("Fields to Encrypt")

        if "encrypt_fields" not in st.session_state:
            st.session_state.encrypt_fields = ["sensitive_data"]

        fields_to_remove = None
        field_list = st.session_state.encrypt_fields
        add_button_placed = False
        for row_start in range(0, len(field_list), 2):
            row_has_pair = (row_start + 1) < len(field_list)
            row_cols = st.columns([3, 1, 3, 1])
            for offset in range(2):
                idx = row_start + offset
                if idx >= len(field_list):
                    break
                field_col = row_cols[offset * 2]
                remove_col = row_cols[offset * 2 + 1]
                with field_col:
                    field_list[idx] = st.text_input(
                        f"Field {idx + 1}",
                        value=field_list[idx],
                        key=f"encrypt_field_{idx}",
                        label_visibility="collapsed",
                        placeholder="e.g. sensitive_data",
                    )
                with remove_col:
                    # Only offer removal if more than one field remains, so
                    # the list can never be emptied down to zero rows.
                    if len(field_list) > 1:
                        if st.button("✕", key=f"remove_field_{idx}"):
                            fields_to_remove = idx

            if not row_has_pair:
                # This row only had one field — use its free half for the
                # Add Field control rather than leaving it blank.
                with row_cols[2]:
                    if st.button("＋ Add Field", key="add_field_btn"):
                        st.session_state.encrypt_fields.append("")
                        st.rerun()
                add_button_placed = True

        if fields_to_remove is not None:
            st.session_state.encrypt_fields.pop(fields_to_remove)
            st.rerun()

        if not add_button_placed:
            if st.button("＋ Add Field", key="add_field_btn"):
                st.session_state.encrypt_fields.append("")
                st.rerun()

        # Build the comma-separated string the backend API expects, from
        # whatever non-empty fields the user has added via the UI above.
        target_fields = ",".join(
            f.strip() for f in st.session_state.encrypt_fields if f.strip()
        )

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
        if st.button("Refresh Active Fields"):
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
        st.subheader("Live Expiry & Retrieval Test")

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
                timer_placeholder.warning(f"**LIVE COUNTDOWN:** `{remaining}s` remaining before cryptographic shredding...")
                time.sleep(1)
                st.rerun()
            else:
                timer_placeholder.warning(f"**KEY ACTIVE:** `{remaining:,}s` remaining before cryptographic shredding...")
        else:
            timer_placeholder.error("**TTL EXPIRED:** Cryptographic key has been mathematically shredded in the Vault.")
