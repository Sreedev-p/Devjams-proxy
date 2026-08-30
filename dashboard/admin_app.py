import time
import datetime
import html
import requests
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="DataExpiry — Vault Console",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# DESIGN TOKENS
# Palette: cold-vault graphite, not the near-black/acid-green hacker default.
#   bg        #0A0C10   base
#   panel     #12151B   surface
#   panel-2   #171B22   raised surface
#   hairline  #23272F   borders
#   ink       #E7E9EC   primary text
#   ink-dim   #7C838F   secondary text
#   signal    #7FD8C8   accent (cold cyan-teal — "live" state)
#   shred     #E5636B   danger / key destruction
#   warn      #E3A85B   caution
# Type: Space Grotesk (display/UI), IBM Plex Sans (body), IBM Plex Mono (data/ledger)
# Signature element: the "entropy pulse" — a live heartbeat dot + ledger rows
# set in tabular mono, treating every timestamp/key/id as literal data, not UI.
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
    --bg: #0A0C10;
    --panel: #12151B;
    --panel-2: #171B22;
    --hairline: #23272F;
    --ink: #E7E9EC;
    --ink-dim: #7C838F;
    --ink-faint: #4B505A;
    --signal: #7FD8C8;
    --signal-dim: rgba(127, 216, 200, 0.12);
    --shred: #E5636B;
    --shred-dim: rgba(229, 99, 107, 0.12);
    --warn: #E3A85B;
    --warn-dim: rgba(227, 168, 91, 0.12);
}

/* ---- base ---- */
.stApp, [data-testid="stSidebar"] { background-color: var(--bg) !important; }
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; color: var(--ink); }
h1, h2, h3, h4, .vc-display { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.01em; }
[data-testid="stHeader"] { background-color: transparent !important; }
#MainMenu, footer { visibility: hidden; }
::selection { background: var(--signal-dim); color: var(--signal); }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulseDot {
    0%   { box-shadow: 0 0 0 0 var(--pulse-color, var(--signal-dim)); }
    70%  { box-shadow: 0 0 0 7px rgba(0,0,0,0); }
    100% { box-shadow: 0 0 0 0 rgba(0,0,0,0); }
}
@keyframes sweep {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(220%); }
}
@keyframes gridDrift {
    0%   { background-position: 0 0; }
    100% { background-position: 40px 40px; }
}

/* ---- eyebrow / section labels ---- */
.vc-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink-faint);
    margin-bottom: 0.35rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.vc-eyebrow::before {
    content: "";
    width: 5px;
    height: 5px;
    background: var(--signal);
    border-radius: 50%;
}

/* ---- live status dot ---- */
.vc-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    margin-right: 7px;
    animation: pulseDot 1.8s infinite;
}
.vc-dot.on   { background: var(--signal); --pulse-color: var(--signal-dim); }
.vc-dot.off  { background: var(--shred);  --pulse-color: var(--shred-dim); }
.vc-dot.warn { background: var(--warn);   --pulse-color: var(--warn-dim); }

.vc-status-line {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: var(--ink-dim);
    display: flex;
    align-items: center;
    padding: 0.5rem 0.65rem;
    background: var(--panel);
    border: 1px solid var(--hairline);
    border-radius: 4px;
}

/* ---- inputs ---- */
.stTextInput input {
    background-color: var(--panel) !important;
    border: 1px solid var(--hairline) !important;
    border-radius: 4px !important;
    color: var(--ink) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
}
.stTextInput input:focus {
    border-color: var(--signal) !important;
    box-shadow: 0 0 0 1px var(--signal) !important;
}
.stTextInput input::placeholder { color: var(--ink-faint) !important; }
label, .stTextInput label p { font-family: 'IBM Plex Mono', monospace !important; font-size: 0.72rem !important; color: var(--ink-dim) !important; letter-spacing: 0.04em; }

/* ---- buttons ---- */
.stButton button {
    background-color: var(--panel-2) !important;
    border: 1px solid var(--hairline) !important;
    color: var(--ink) !important;
    border-radius: 4px !important;
    width: 100% !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.03em;
    padding: 0.55rem 0.8rem !important;
    transition: border-color 0.15s ease, transform 0.1s ease, color 0.15s ease;
}
.stButton button:hover {
    border-color: var(--signal) !important;
    color: var(--signal) !important;
    transform: translateY(-1px);
}
.stButton button:active { transform: translateY(0); }

/* Primary / danger buttons are targeted via their Streamlit `key`, not a
   markdown div-wrap — a div opened in one st.markdown() and closed in
   another never actually nests the widgets between them (each call is a
   separate DOM sibling), so that old trick rendered as an empty box and
   never touched the button at all. Streamlit gives widgets created with
   `key=` a wrapper class of the form `st-key-<key>`, which we can target
   directly and reliably. Requires streamlit >= 1.35. */
[class*="st-key-auth_btn"] button,
[class*="st-key-deploy_btn"] button,
[class*="st-key-pull_btn"] button {
    background-color: var(--signal) !important;
    border: 1px solid var(--signal) !important;
    color: #061412 !important;
    font-weight: 600 !important;
}
[class*="st-key-auth_btn"] button:hover,
[class*="st-key-deploy_btn"] button:hover,
[class*="st-key-pull_btn"] button:hover {
    background-color: #93E3D4 !important;
    color: #061412 !important;
    border-color: #93E3D4 !important;
}
[class*="st-key-rm_"] button {
    color: var(--shred) !important;
    border-color: var(--shred-dim) !important;
    background: transparent !important;
}
[class*="st-key-rm_"] button:hover { border-color: var(--shred) !important; }

/* ---- tabs -> premium segmented control ----
   The old red line was Streamlit's default tab-highlight indicator bar
   (baseweb's built-in sliding underline, in the theme's primary color).
   `.stTabs [data-baseweb="tab-highlight"]` was too narrow a selector to
   reliably catch it, so it kept showing through. Since data-baseweb
   attributes are unique to this component, we target them directly and
   kill the element outright rather than trying to recolor it — the pill
   fill on the active tab is the indicator now, there's nothing sliding
   underneath it to hide. */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--panel);
    padding: 4px;
    border-radius: 8px;
    border: 1px solid var(--hairline);
    width: fit-content;
}
[data-testid="stTabs"] button[data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem;
    letter-spacing: 0.05em;
    color: var(--ink-dim);
    background: transparent !important;
    border-radius: 6px;
    padding: 9px 20px;
    transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
}
[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
    color: var(--ink);
    background: rgba(255,255,255,0.035) !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    background: var(--panel-2) !important;
    color: var(--signal) !important;
    box-shadow: inset 0 0 0 1px rgba(127, 216, 200, 0.28);
}
[data-testid="stTabs"] button[aria-selected="true"] p { color: var(--signal) !important; }
[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] {
    display: none !important;
    height: 0 !important;
    opacity: 0 !important;
    background: transparent !important;
}
[data-testid="stTabs"] [data-testid="stTabsPanel"] { padding-top: 1.1rem; }


/* ---- containers as vault slots ---- */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-color: var(--hairline) !important;
    background: var(--panel) !important;
    border-radius: 6px !important;
}

/* ---- alerts, restyled thin ---- */
[data-testid="stAlert"] {
    background: var(--panel) !important;
    border: 1px solid var(--hairline) !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
}

hr { border-color: var(--hairline) !important; }

/* ---- custom metric cards ---- */
.vc-metric-row { display: flex; gap: 12px; margin: 0.4rem 0 1rem 0; }
.vc-metric {
    flex: 1;
    background: var(--panel);
    border: 1px solid var(--hairline);
    border-radius: 6px;
    padding: 16px 18px;
    animation: fadeUp 0.4s ease both;
}
.vc-metric:nth-child(1) { animation-delay: 0.02s; }
.vc-metric:nth-child(2) { animation-delay: 0.08s; }
.vc-metric:nth-child(3) { animation-delay: 0.14s; }
.vc-metric:nth-child(4) { animation-delay: 0.20s; }
.vc-metric .label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--ink-dim);
    margin-bottom: 6px;
}
.vc-metric .value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.9rem;
    font-weight: 500;
    font-variant-numeric: tabular-nums;
}
.vc-metric.signal .value { color: var(--signal); }
.vc-metric.shred .value  { color: var(--shred); }
.vc-metric.warn .value   { color: var(--warn); }

/* ---- ledger table ---- */
.vc-ledger { width: 100%; border-collapse: collapse; font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; animation: fadeUp 0.45s ease both; }
.vc-ledger thead th {
    text-align: left;
    padding: 8px 12px;
    color: var(--ink-faint);
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border-bottom: 1px solid var(--hairline);
}
.vc-ledger tbody td {
    padding: 8px 12px;
    border-bottom: 1px solid var(--hairline);
    color: var(--ink);
}
.vc-ledger tbody tr { transition: background 0.12s ease; }
.vc-ledger tbody tr:hover { background: var(--panel-2); }
.vc-ledger .ts { color: var(--ink-dim); font-variant-numeric: tabular-nums; }
.vc-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 0.72rem;
}
.vc-badge.gen   { background: var(--signal-dim); color: var(--signal); }
.vc-badge.shred { background: var(--shred-dim); color: var(--shred); }
.vc-badge.read  { background: rgba(127,178,216,0.12); color: #7FB2D8; }
.vc-badge.cfg   { background: var(--warn-dim); color: var(--warn); }

/* ---- sweep loader ---- */
.vc-sweep-track { position: relative; height: 2px; background: var(--hairline); border-radius: 2px; overflow: hidden; margin: 0.5rem 0 1rem 0; }
.vc-sweep-bar { position: absolute; top: 0; left: 0; width: 30%; height: 100%; background: linear-gradient(90deg, transparent, var(--signal), transparent); animation: sweep 1.1s linear infinite; }

/* ---- gateway ---- */
/* Gate card: a real st.container(border=True, key="gate_card") so its
   contents genuinely nest inside it — scoped with the same key-class
   technique used for the buttons above. The dotted grid lives on the
   page behind the card (see gate-screen style block), not squeezed into
   the card's own border, so the edge stays a single clean hairline. */
[class*="st-key-gate_card"] [data-testid="stVerticalBlockBorderWrapper"] > div {
    background: var(--panel) !important;
    border: 1px solid var(--hairline) !important;
    border-radius: 10px !important;
    padding: 42px 38px 34px 38px !important;
    position: relative;
    overflow: hidden;
    box-shadow: 0 24px 60px -24px rgba(0,0,0,0.65);
    animation: fadeUp 0.5s ease both;
}
[class*="st-key-gate_card"] [data-testid="stVerticalBlockBorderWrapper"] > div::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--signal), transparent);
    opacity: 0.7;
}
[class*="st-key-auth_btn"] button { width: 100% !important; }
.vc-gate-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: 600; margin-bottom: 2px; }
.vc-gate-sub { font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; color: var(--ink-dim); margin-bottom: 24px; }
</style>
""", unsafe_allow_html=True)


def render_status_dot(state: str, label: str) -> str:
    cls = {"on": "on", "off": "off", "warn": "warn"}.get(state, "off")
    return f'<span class="vc-dot {cls}"></span>{label}'


# ==========================================
# AUTHENTICATION GATEWAY
# ==========================================
if "portal_unlocked" not in st.session_state:
    st.session_state.portal_unlocked = False

if not st.session_state.portal_unlocked:
    st.markdown("""
    <style>
    .stApp {
        background-image: radial-gradient(var(--hairline) 1px, transparent 1px) !important;
        background-size: 28px 28px !important;
        animation: gridDrift 8s linear infinite;
    }
    </style>
    """, unsafe_allow_html=True)
    st.write("")
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([1.2, 1, 1.2])
    with col2:
        with st.container(border=True, key="gate_card"):
            st.markdown('<div class="vc-eyebrow">Zero-trust gateway</div>', unsafe_allow_html=True)
            st.markdown('<div class="vc-gate-title">◈ Vault Console</div>', unsafe_allow_html=True)
            st.markdown('<div class="vc-gate-sub">Authenticate to access SOC telemetry.</div>', unsafe_allow_html=True)

            pwd = st.text_input(
                "Administrator Password", type="password",
                label_visibility="collapsed", placeholder="enter passphrase",
            )

            if st.button("Authenticate Session →", key="auth_btn"):
                if pwd == "soc_admin_2026":
                    st.session_state.portal_unlocked = True
                    st.rerun()
                else:
                    st.error("Invalid credentials — access not granted.")
    st.stop()

# --- STATE INITIALIZATION ---
if "encrypt_fields" not in st.session_state:
    st.session_state.encrypt_fields = []
if "admin_key" not in st.session_state:
    st.session_state.admin_key = "hackathon_admin_99"
if "proxy_url" not in st.session_state:
    st.session_state.proxy_url = "http://127.0.0.1:8000"


def get_headers():
    return {"X-Admin-Key": st.session_state.admin_key, "User-Agent": "DataExpiry-AdminPanel/3.0"}


# ==========================================
# SIDEBAR — console rail
# ==========================================
with st.sidebar:
    st.markdown('<div class="vc-eyebrow">DataExpiry</div>', unsafe_allow_html=True)
    st.markdown('<div class="vc-display" style="font-size:1.25rem; font-weight:600; margin-bottom:1.2rem;">◈ SOC Console</div>', unsafe_allow_html=True)

    st.markdown('<div class="vc-eyebrow">Network configuration</div>', unsafe_allow_html=True)
    st.session_state.proxy_url = st.text_input("Proxy Host", value=st.session_state.proxy_url)
    st.session_state.admin_key = st.text_input("Admin API Key", type="password", value=st.session_state.admin_key)

    st.write("")
    st.markdown('<div class="vc-eyebrow">Upstream health</div>', unsafe_allow_html=True)
    try:
        res = requests.get(f"{st.session_state.proxy_url}/api/admin/config", headers=get_headers(), timeout=2)
        if res.status_code == 200:
            st.markdown(f'<div class="vc-status-line">{render_status_dot("on", "Cryptographic engine online")}</div>', unsafe_allow_html=True)
        elif res.status_code == 401:
            st.markdown(f'<div class="vc-status-line">{render_status_dot("off", "Unauthorized request")}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="vc-status-line">{render_status_dot("warn", f"HTTP {res.status_code}")}</div>', unsafe_allow_html=True)
    except Exception:
        st.markdown(f'<div class="vc-status-line">{render_status_dot("off", "Engine unreachable")}</div>', unsafe_allow_html=True)

# ==========================================
# MAIN DASHBOARD
# ==========================================
st.markdown('<div class="vc-eyebrow">Command center</div>', unsafe_allow_html=True)
st.markdown('<h1 style="margin-top:-8px; margin-bottom:2px;">SOC Command Center</h1>', unsafe_allow_html=True)
st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.82rem; color:var(--ink-dim); margin-bottom:1.3rem;">Monitor active encryption matrices and manage Data Loss Prevention (DLP) rulesets.</div>', unsafe_allow_html=True)
st.markdown('<hr>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["◆ POLICY MANAGEMENT", "◆ REAL-TIME TELEMETRY"])

# --- MODULE A: DLP POLICY MANAGER ---
with tab1:
    col_title, col_sync = st.columns([3, 1])
    with col_title:
        st.markdown('<div class="vc-eyebrow">Active ruleset</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Space Grotesk\',sans-serif; font-size:1.15rem; font-weight:600; margin-bottom:2px;">DLP Interception Rules</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.78rem; color:var(--ink-dim);">JSON payload keys intercepted and encrypted before reaching the database.</div>', unsafe_allow_html=True)
    with col_sync:
        st.write("")
        if st.button("↻ Sync Upstream"):
            try:
                res = requests.get(f"{st.session_state.proxy_url}/api/admin/config", headers=get_headers(), timeout=5)
                if res.status_code == 200:
                    st.session_state.encrypt_fields = res.json().get("active_fields", [])
                    st.toast("Rules synced with proxy.", icon="✅")
                else:
                    st.error("Sync failed.")
            except Exception:
                st.error("Network error.")
    st.write("")

    with st.container(border=True):
        fields_to_remove = None

        if not st.session_state.encrypt_fields:
            st.markdown(
                f'<div class="vc-status-line">{render_status_dot("warn", "No active interception rules — all data flows in plaintext.")}</div>',
                unsafe_allow_html=True,
            )

        for idx, value in enumerate(st.session_state.encrypt_fields):
            col_tag, col_input, col_btn = st.columns([0.3, 4.7, 1])
            with col_tag:
                st.markdown(f'<div style="font-family:\'IBM Plex Mono\',monospace; color:var(--ink-faint); font-size:0.75rem; padding-top:0.55rem;">{idx:02d}</div>', unsafe_allow_html=True)
            with col_input:
                st.session_state.encrypt_fields[idx] = st.text_input(
                    f"field_{idx}",
                    value=value,
                    label_visibility="collapsed",
                    placeholder="e.g. ssn, credit_card",
                )
            with col_btn:
                if st.button("Remove", key=f"rm_{idx}"):
                    fields_to_remove = idx

        if fields_to_remove is not None:
            st.session_state.encrypt_fields.pop(fields_to_remove)
            st.rerun()

        st.write("")
        col_add, col_deploy = st.columns(2)
        with col_add:
            if st.button("+ Add Target Field"):
                st.session_state.encrypt_fields.append("")
                st.rerun()

        with col_deploy:
            if st.button("⬆ Deploy Ruleset to Proxy", key="deploy_btn"):
                target_fields = ",".join([f.strip() for f in st.session_state.encrypt_fields if f.strip()])
                try:
                    res = requests.post(
                        f"{st.session_state.proxy_url}/api/admin/config",
                        json={"fields": target_fields},
                        headers=get_headers(),
                        timeout=5,
                    )
                    if res.status_code in (200, 201):
                        st.success("Rules deployed successfully.")
                    else:
                        st.error("Deployment failed.")
                except Exception:
                    st.error("Network error.")

# --- MODULE B: SOC TELEMETRY ---
with tab2:
    st.markdown('<div class="vc-eyebrow">Audit trail</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Space Grotesk\',sans-serif; font-size:1.15rem; font-weight:600; margin-bottom:2px;">Cryptographic Event Ledger</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.78rem; color:var(--ink-dim); margin-bottom:0.8rem;">Immutable append-only log of DEK generations, shreds, and access attempts.</div>', unsafe_allow_html=True)

    fetch_data = st.button("⬇ Pull Latest Telemetry Data", key="pull_btn")

    if fetch_data:
        sweep_placeholder = st.empty()
        sweep_placeholder.markdown(
            '<div class="vc-sweep-track"><div class="vc-sweep-bar"></div></div>'
            '<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.72rem; color:var(--ink-dim); margin-bottom:1rem;">reading cryptographic ledger…</div>',
            unsafe_allow_html=True,
        )
        try:
            res = requests.get(f"{st.session_state.proxy_url}/api/admin/logs?limit=100", headers=get_headers(), timeout=5)
            sweep_placeholder.empty()

            if res.status_code == 200:
                data = res.json()
                summary = data.get("summary", {})
                logs = data.get("logs", [])

                active_keys = html.escape(str(summary.get("active_keys", 0)))
                shredded_keys = html.escape(str(summary.get("shredded_keys", 0)))
                decryption_attempts = html.escape(str(summary.get("decryption_attempts", 0)))
                total_events = html.escape(str(summary.get("total_events", len(logs))))

                st.markdown(f"""
                <div class="vc-metric-row">
                    <div class="vc-metric signal"><div class="label">Active DEKs</div><div class="value">{active_keys}</div></div>
                    <div class="vc-metric shred"><div class="label">Shredded Keys</div><div class="value">{shredded_keys}</div></div>
                    <div class="vc-metric warn"><div class="label">Read Attempts</div><div class="value">{decryption_attempts}</div></div>
                    <div class="vc-metric"><div class="label">Total Audits</div><div class="value">{total_events}</div></div>
                </div>
                """, unsafe_allow_html=True)

                if logs:
                    df = pd.DataFrame(logs)
                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s").dt.strftime("%H:%M:%S · %Y-%m-%d")

                    badge_map = {
                        "KEY_GENERATED": ("gen", "● KEY_GENERATED"),
                        "KEY_SHREDDED": ("shred", "● KEY_SHREDDED"),
                        "DECRYPTION_ATTEMPT": ("read", "● DECRYPT_CALL"),
                        "CONFIG_UPDATED": ("cfg", "● CONFIG_UPDATE"),
                    }

                    rows_html = ""
                    for _, row in df.iterrows():
                        cls, raw_label = badge_map.get(row["event_type"], ("read", row["event_type"]))
                        safe_label = raw_label if row["event_type"] in badge_map else f"● {html.escape(str(raw_label))}"
                        safe_data_id = html.escape(str(row.get("data_id", "")))
                        rows_html += f"""
                        <tr>
                            <td class="ts">{row['timestamp']}</td>
                            <td><span class="vc-badge {cls}">{safe_label}</span></td>
                            <td>{safe_data_id}</td>
                        </tr>"""

                    table_html = f"""
                    <table class="vc-ledger">
                        <thead>
                            <tr><th>Timestamp</th><th>Event</th><th>Data ID</th></tr>
                        </thead>
                        <tbody>{rows_html}</tbody>
                    </table>
                    """
                    st.markdown(table_html, unsafe_allow_html=True)
                else:
                    st.markdown(
                        f'<div class="vc-status-line">{render_status_dot("warn", "No cryptographic events recorded yet.")}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.error("Failed to fetch telemetry.")
        except Exception:
            sweep_placeholder.empty()
            st.error("Engine unreachable.")
