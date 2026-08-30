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

# --- GITHUB DARK THEME TOKENS ---
THEME = {
    "bg": "#0d1117",              # GitHub Canvas
    "surface": "#161b22",         # GitHub Card
    "surface_alt": "#21262d",     # Secondary background
    "border": "#30363d",          # GitHub Border
    "text": "#c9d1d9",            # Primary text
    "muted": "#8b949e",           # Secondary text
    "accent": "#2f81f7",          # GitHub Blue (Links/Active)
    "accent_hover": "#58a6ff",
    "critical": "#f85149",        # GitHub Red (Danger)
    "success": "#238636",         # GitHub Green (Primary Button)
    "success_hover": "#2ea043",
    "warning": "#d29922",         # GitHub Yellow
}

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
        background-color: {THEME["bg"]};
        color: {THEME["text"]};
    }}

    .stApp {{ background: {THEME["bg"]}; }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}

    /* Headers & Text */
    h1, h2, h3, h4, h5, h6 {{ 
        color: {THEME["text"]} !important; 
        font-weight: 600 !important;
    }}
    p, label, .stMarkdown, .stCaption {{ color: {THEME["text"]}; }}
    .mono {{ font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, monospace; }}

    /* Inputs (Text, Password, Select) */
    .stTextInput input, div[data-baseweb="base-input"] {{
        background-color: {THEME["bg"]} !important;
        color: {THEME["text"]} !important;
        border: 1px solid {THEME["border"]} !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        padding: 6px 12px !important;
        transition: border-color 0.2s cubic-bezier(0.3, 0, 0.5, 1);
    }}
    .stTextInput input:focus, div[data-baseweb="base-input"]:focus-within {{
        border-color: {THEME["accent"]} !important;
        box-shadow: 0 0 0 2px rgba(47, 129, 247, 0.3) !important;
    }}

    /* Base Buttons (GitHub Secondary) */
    .stButton button {{
        background-color: {THEME["surface_alt"]} !important;
        color: {THEME["text"]} !important;
        border: 1px solid rgba(240, 246, 252, 0.1) !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: 80ms cubic-bezier(0.33, 1, 0.68, 1);
    }}
    .stButton button:hover {{
        background-color: #30363d !important;
        border-color: {THEME["muted"]} !important;
    }}

    /* Primary Actions (GitHub Green) */
    .primary-btn .stButton button {{
        background-color: {THEME["success"]} !important;
        color: #ffffff !important;
        border: 1px solid rgba(240, 246, 252, 0.1) !important;
    }}
    .primary-btn .stButton button:hover {{
        background-color: {THEME["success_hover"]} !important;
    }}

    /* Containers & Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {THEME["bg"]};
        border: 1px solid {THEME["border"]};
        border-radius: 6px;
    }}

    /* Metric Cards */
    [data-testid="stMetric"] {{
        background-color: {THEME["surface"]};
        border: 1px solid {THEME["border"]};
        border-radius: 6px;
        padding: 16px;
    }}
    [data-testid="stMetricLabel"] * {{
        color: {THEME["muted"]} !important;
        font-size: 12px !important;
        font-weight: 500 !important;
    }}
    [data-testid="stMetricValue"] * {{
        color: {THEME["text"]} !important;
        font-weight: 600 !important;
        font-size: 24px !important;
    }}

    /* DataFrames & JSON */
    .stDataFrame, .stJson {{
        border: 1px solid {THEME["border"]};
        border-radius: 6px;
        background-color: {THEME["surface"]};
    }}

    /* Badges */
    .badge-amber {{ color: {THEME["warning"]}; font-weight: 600; font-family: 'JetBrains Mono', monospace; font-size: 13px; }}
    .badge-red {{ color: {THEME["critical"]}; font-weight: 600; font-family: 'JetBrains Mono', monospace; font-size: 13px; }}
    .badge-blue {{ color: {THEME["accent"]}; font-weight: 600; font-family: 'JetBrains Mono', monospace; font-size: 13px; }}

    hr {{ border-color: {THEME["border"]} !important; margin: 24px 0 !important; }}
    
    /* Tabs (Simulating GitHub Repository Nav) */
    button[data-baseweb="tab"] {{
        background-color: transparent !important;
        color: {THEME["muted"]} !important;
        border-radius: 0 !important;
        border-bottom: 2px solid transparent !important;
        font-weight: 500 !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {THEME["text"]} !important;
        border-bottom: 2px solid #fd8c73 !important; /* GitHub repo tab accent */
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# APP-LEVEL SECURITY GATE
# ==========================================
if "portal_unlocked" not in st.session_state:
    st.session_state.portal_unlocked = False

if not st.session_state.portal_unlocked:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.container(border=True):
            st.markdown("### sudo required")
            st.caption("Verify your access to continue to the SOC dashboard.")
            pwd = st.text_input("Password", type="password")
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Confirm access", use_container_width=True):
                if pwd == "soc_admin_2026": 
                    st.session_state.portal_unlocked = True
                    st.rerun()
                else:
                    st.error("Invalid password.")
            st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# --- STATE INITIALIZATION ---
if "encrypt_fields" not in st.session_state:
    st.session_state.encrypt_fields = []
if "admin_key" not in st.session_state:
    st.session_state.admin_key = "hackathon_admin_99"
if "proxy_url" not in st.session_state:
    # Changed to localhost to enforce local routing (bypassing Ngrok latency)
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
    st.markdown("### ⚙️ Environment")
    st.session_state.proxy_url = st.text_input("Proxy Host", value=st.session_state.proxy_url)
    st.session_state.admin_key = st.text_input("Admin API Key", type="password", value=st.session_state.admin_key)
    
    st.markdown("---")
    st.markdown("### 🔒 Upstream Status")
    try:
        res = requests.get(f"{st.session_state.proxy_url}/api/admin/config", headers=get_headers(), timeout=3)
        if res.status_code == 200:
            st.success("Connected to Proxy Engine")
        elif res.status_code == 401:
            st.error("401 Unauthorized (Check API Key)")
        else:
            st.warning(f"HTTP {res.status_code}")
    except:
        st.error("ERR_CONNECTION_REFUSED")

# --- MAIN UI ---
st.title("Admin & SOC Control Panel")
st.markdown("Configure DataExpiry interception policies and monitor vault telemetry.")
st.markdown("---")

tab1, tab2 = st.tabs(["🛡️ Policy Management", "📊 Audit Logs"])

# ==========================================
# MODULE A: DLP POLICY MANAGER
# ==========================================
with tab1:
    st.markdown("#### Data Loss Prevention Rules")
    st.caption("JSON payload fields matching these definitions will be intercepted and envelope-encrypted at the edge.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Fetch Current Configuration", use_container_width=True):
            try:
                res = requests.get(f"{st.session_state.proxy_url}/api/admin/config", headers=get_headers(), timeout=10)
                if res.status_code == 200:
                    st.session_state.encrypt_fields = res.json().get("active_fields", [])
                    st.toast("Configuration pulled successfully.", icon="✅")
                else:
                    st.error(f"Fetch failed: HTTP {res.status_code}")
            except Exception as e:
                st.error(f"Network error: {e}")

    with st.container(border=True):
        st.markdown("**Target Fields**")
        
        fields_to_remove = None
        for idx, value in enumerate(st.session_state.encrypt_fields):
            a, b = st.columns([5, 1])
            with a:
                st.session_state.encrypt_fields[idx] = st.text_input(
                    f"Field {idx + 1}", 
                    value=value, 
                    key=f"field_{idx}",
                    label_visibility="collapsed",
                    placeholder="e.g. ssn, credit_card"
                )
            with b:
                if st.button("Remove", key=f"rm_{idx}", use_container_width=True):
                    fields_to_remove = idx
                    
        if fields_to_remove is not None:
            st.session_state.encrypt_fields.pop(fields_to_remove)
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("+ Add new field", use_container_width=True):
                st.session_state.encrypt_fields.append("")
                st.rerun()
                
        with btn_col2:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Commit changes", use_container_width=True):
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
                        st.success("Configuration committed to edge proxy.")
                    elif res.status_code == 401:
                        st.error("Unauthorized: Invalid API Key.")
                    else:
                        st.error(f"Commit failed: HTTP {res.status_code}")
                except Exception as e:
                    st.error(f"Network error: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# MODULE B: SOC TELEMETRY & AUDIT TRAIL
# ==========================================
with tab2:
    st.markdown("#### Cryptographic Event Ledger")
    st.caption("Immutable append-only logs for all DEK generations, shreds, and decryption access attempts.")
    
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
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
                m1.metric("Active Keys (Vault)", summary.get("active_keys", 0))
                m2.metric("Shredded Keys", summary.get("shredded_keys", 0))
                m3.metric("Decryption Attempts", summary.get("decryption_attempts", 0))
                m4.metric("Total Vault Events", summary.get("total_events", len(logs)))
                
                st.markdown("---")
                
                if logs:
                    df = pd.DataFrame(logs)
                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='s').dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    def format_event(event):
                        if event == "KEY_GENERATED": return "🟡 KEY_GENERATED"
                        elif event == "KEY_SHREDDED": return "🔴 KEY_SHREDDED"
                        elif event == "DECRYPTION_ATTEMPT": return "🔵 DECRYPTION_ATTEMPT"
                        return f"⚪ {event}"
                        
                    df["event_type"] = df["event_type"].apply(format_event)
                    
                    st.dataframe(
                        df[["timestamp", "event_type", "data_id"]],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "timestamp": st.column_config.TextColumn("Timestamp (Local)", width="medium"),
                            "event_type": st.column_config.TextColumn("Event Trigger", width="medium"),
                            "data_id": st.column_config.TextColumn("Envelope UUID", width="large")
                        }
                    )
                    
                    with st.expander("View raw payload (JSON)"):
                        st.json(logs)
                else:
                    st.info("The event ledger is currently empty.")
            
            elif res.status_code == 401:
                st.error("Unauthorized: Invalid API Key.")
            else:
                st.error(f"HTTP {res.status_code}: {res.text}")
                
        except Exception as e:
            st.error(f"Network error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
