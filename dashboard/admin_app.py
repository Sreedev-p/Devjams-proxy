import time
import datetime
import requests
import pandas as pd
import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DataExpiry SOC Admin",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- DESIGN SYSTEM TOKENS ---
THEME = {
    "bg": "#0B0B09",
    "surface": "#151512",
    "border": "#2C2B24",
    "text": "#F3F2EC",
    "accent": "#F5D033",      # Electric Amber
    "critical": "#FF4D5E",    # Crimson Red
    "info": "#3E7BFA",        # Cobalt Blue
    "muted": "#8B96A5",
}

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: {THEME["bg"]};
        color: {THEME["text"]};
    }}

    .stApp {{ background: {THEME["bg"]}; }}
    
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}

    /* Typography */
    h1, h2, h3 {{ color: {THEME["text"]} !important; }}
    p, label, .stMarkdown, .stCaption {{ color: {THEME["text"]}; }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    /* Inputs */
    .stTextInput input, div[data-baseweb="base-input"] {{
        background: {THEME["bg"]} !important;
        color: {THEME["text"]} !important;
        border: 1px solid {THEME["border"]} !important;
        border-radius: 8px !important;
    }}
    .stTextInput input:focus, div[data-baseweb="base-input"]:focus-within {{
        border-color: {THEME["accent"]} !important;
        box-shadow: 0 0 0 1px {THEME["accent"]} !important;
    }}

    /* Buttons */
    .stButton button {{
        background: {THEME["surface"]} !important;
        color: {THEME["text"]} !important;
        border: 1px solid {THEME["border"]} !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
    }}
    .stButton button:hover {{
        border-color: {THEME["accent"]} !important;
        color: {THEME["accent"]} !important;
    }}
    
    /* Primary Accent Button */
    .primary-btn .stButton button {{
        background: {THEME["accent"]} !important;
        color: #000000 !important;
        border: none !important;
    }}
    .primary-btn .stButton button:hover {{
        filter: brightness(1.1);
    }}

    /* Metric Cards */
    [data-testid="stMetric"] {{
        background: {THEME["surface"]};
        border: 1px solid {THEME["border"]};
        border-radius: 12px;
        padding: 16px 20px;
    }}
    [data-testid="stMetricLabel"] * {{
        color: {THEME["muted"]} !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    [data-testid="stMetricValue"] * {{
        color: {THEME["text"]} !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.8rem !important;
    }}

    /* Containers & DataFrames */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {THEME["surface"]};
        border: 1px solid {THEME["border"]};
        border-radius: 12px;
    }}
    .stDataFrame, .stJson {{
        border: 1px solid {THEME["border"]};
        border-radius: 8px;
    }}
    
    /* Event Badges */
    .badge-amber {{ color: {THEME["accent"]}; font-weight: 600; }}
    .badge-red {{ color: {THEME["critical"]}; font-weight: 600; }}
    .badge-blue {{ color: {THEME["info"]}; font-weight: 600; }}
    .badge-gray {{ color: {THEME["muted"]}; font-weight: 600; }}

    hr {{ border-color: {THEME["border"]} !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- STATE INITIALIZATION ---
if "encrypt_fields" not in st.session_state:
    st.session_state.encrypt_fields = []
if "admin_key" not in st.session_state:
    st.session_state.admin_key = "hackathon_admin_99"
if "proxy_url" not in st.session_state:
    st.session_state.proxy_url = "http://localhost:8000"

def get_headers():
    return {
        "X-Admin-Key": st.session_state.admin_key,
        "Bypass-Tunnel-Reminder": "true",
        "ngrok-skip-browser-warning": "true",
        "User-Agent": "DataExpiry-AdminPanel/1.0"
    }

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.markdown("### ⚙️ Connection Settings")
    st.session_state.proxy_url = st.text_input("Proxy URL", value=st.session_state.proxy_url)
    st.session_state.admin_key = st.text_input("Admin API Key", type="password", value=st.session_state.admin_key)
    
    st.markdown("---")
    st.markdown("### 🔒 System Status")
    try:
        res = requests.get(f"{st.session_state.proxy_url}/api/admin/config", headers=get_headers(), timeout=3)
        if res.status_code == 200:
            st.success("Proxy Online")
        elif res.status_code == 401:
            st.error("Unauthorized (Check Key)")
        else:
            st.warning(f"Error {res.status_code}")
    except:
        st.error("Proxy Unreachable")

# --- MAIN UI ---
st.title("Admin & SOC Control Panel")
st.markdown("Enterprise-grade management for DataExpiry cryptographic erasure and telemetry.")

tab1, tab2 = st.tabs(["🛡️ DLP Policy Manager", "📊 SOC Telemetry & Audit"])

# ==========================================
# MODULE A: DLP POLICY MANAGER
# ==========================================
with tab1:
    st.subheader("Data Loss Prevention (DLP) Policies")
    st.caption("Define the exact JSON payload fields to be intercepted and enveloped by the proxy.")
    
    # Fetch current config
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🔄 Sync with Proxy", use_container_width=True):
            try:
                res = requests.get(f"{st.session_state.proxy_url}/api/admin/config", headers=get_headers(), timeout=10)
                if res.status_code == 200:
                    st.session_state.encrypt_fields = res.json().get("active_fields", [])
                    st.toast("Policy synced successfully.", icon="✅")
                else:
                    st.error(f"Failed to fetch config: {res.status_code}")
            except Exception as e:
                st.error(f"Connection failed: {e}")

    with st.container(border=True):
        st.markdown("### Active Encryption Fields")
        
        # Interactive Field Manager
        fields_to_remove = None
        for idx, value in enumerate(st.session_state.encrypt_fields):
            a, b = st.columns([5, 1])
            with a:
                st.session_state.encrypt_fields[idx] = st.text_input(
                    f"Field {idx + 1}", 
                    value=value, 
                    key=f"field_{idx}",
                    label_visibility="collapsed"
                )
            with b:
                if st.button("✕ Remove", key=f"rm_{idx}", use_container_width=True):
                    fields_to_remove = idx
                    
        if fields_to_remove is not None:
            st.session_state.encrypt_fields.pop(fields_to_remove)
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("+ Add Field", use_container_width=True):
                st.session_state.encrypt_fields.append("")
                st.rerun()
                
        with btn_col2:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("💾 Commit Policy to Proxy", use_container_width=True):
                target_fields = ",".join([f.strip() for f in st.session_state.encrypt_fields if f.strip()])
                payload = {"fields": target_fields}
                try:
                    res = requests.post(
                        f"{st.session_state.proxy_url}/api/admin/config",
                        json=payload,
                        headers=get_headers(),
                        timeout=10
                    )
                    if res.status_code in (200, 201):
                        st.success("Policy successfully enforced at the edge.")
                    elif res.status_code == 401:
                        st.error("Unauthorized: Invalid Admin Key.")
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# MODULE B: SOC TELEMETRY & AUDIT TRAIL
# ==========================================
with tab2:
    st.subheader("Security Information and Event Management (SIEM)")
    st.caption("Immutable cryptographic event ledger and vault telemetry.")
    
    if st.button("Fetch Live Telemetry", use_container_width=True):
        try:
            res = requests.get(f"{st.session_state.proxy_url}/api/admin/logs?limit=200", headers=get_headers(), timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                summary = data.get("summary", {})
                logs = data.get("logs", [])
                
                # Metrics Cards
                st.markdown("<br>", unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Active Encrypted Keys", summary.get("active_keys", 0))
                m2.metric("Crypto-Shredded Keys", summary.get("shredded_keys", 0))
                m3.metric("Decryption Attempts", summary.get("decryption_attempts", 0))
                m4.metric("Total Crypto Events", summary.get("total_events", len(logs)))
                
                st.markdown("---")
                st.markdown("### 📜 Immutable Audit Event Ledger")
                
                if logs:
                    # Data preparation for the ledger
                    df = pd.DataFrame(logs)
                    
                    # Convert UNIX epoch to human readable
                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='s').dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Add UI-friendly indicators for event types
                    def format_event(event):
                        if event == "KEY_GENERATED":
                            return "🟡 KEY_GENERATED"
                        elif event == "KEY_SHREDDED":
                            return "🔴 KEY_SHREDDED"
                        elif event == "DECRYPTION_ATTEMPT":
                            return "🔵 DECRYPTION_ATTEMPT"
                        return f"⚪ {event}"
                        
                    df["event_type"] = df["event_type"].apply(format_event)
                    
                    # Display datagrid
                    st.dataframe(
                        df[["timestamp", "event_type", "data_id"]],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "timestamp": st.column_config.TextColumn("Local Time", width="medium"),
                            "event_type": st.column_config.TextColumn("Cryptographic Event", width="medium"),
                            "data_id": st.column_config.TextColumn("Target Data ID", width="large")
                        }
                    )
                    
                    # Details Expander
                    with st.expander("🔍 Inspect Raw Event Payloads (JSON)"):
                        st.json(logs)
                else:
                    st.info("No cryptographic events recorded in the current timeframe.")
            
            elif res.status_code == 401:
                st.error("Unauthorized: Invalid Admin API Key.")
            else:
                st.error(f"Error fetching logs: {res.status_code} - {res.text}")
                
        except Exception as e:
            st.error(f"Failed to connect to proxy backend: {e}")
