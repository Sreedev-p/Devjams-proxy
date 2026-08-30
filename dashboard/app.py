import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="DataExpiry",
    page_icon="▪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PROXY_URL = "https://latrine-primal-retired.ngrok-free.dev"
BACKEND_URL = "https://rare-bobcats-work.loca.lt"

TUNNEL_HEADERS = {
    "Bypass-Tunnel-Reminder": "true",
    "ngrok-skip-browser-warning": "true",
    "User-Agent": "DataExpiry-App/1.0",
}

# ---------------------------------------------------------------------------
# Design system
#
# A light, confident product surface built for a security tool: near-white
# canvas, a single decisive accent (indigo), and two semantic colors used
# only where they mean something (safe / critical). Fraunces carries the
# headline voice; Inter carries everything else; a monospace face is
# reserved strictly for data that is actually data — record IDs, countdown
# numerals, raw payloads — never for labels or buttons.
# ---------------------------------------------------------------------------
THEME = {
    "bg": "#FAFAFA",
    "surface": "#FFFFFF",
    "surface_sunken": "#F4F4F6",
    "border": "#E4E4E8",
    "border_strong": "#D4D4DA",
    "text": "#18181B",
    "muted": "#71717A",
    "faint": "#A1A1AA",
    "primary": "#4F46E5",
    "primary_hover": "#4338CA",
    "primary_soft": "rgba(79, 70, 229, 0.08)",
    "primary_ring": "rgba(79, 70, 229, 0.16)",
    "safe": "#15803D",
    "safe_soft": "rgba(21, 128, 61, 0.09)",
    "warning": "#B45309",
    "warning_soft": "rgba(180, 83, 9, 0.10)",
    "critical": "#B91C1C",
    "critical_soft": "rgba(185, 28, 28, 0.09)",
}

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, sans-serif;
    }}

    .stApp {{
        background: {THEME["bg"]};
        color: {THEME["text"]};
    }}

    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    [data-testid="stAppViewContainer"] {{ background: {THEME["bg"]}; }}

    .block-container {{
        padding-top: 2.25rem;
        padding-bottom: 4rem;
        max-width: 1120px;
    }}

    h1, h2, h3 {{ color: {THEME["text"]} !important; }}
    p, label, .stMarkdown {{ color: {THEME["text"]}; }}

    ::selection {{ background: {THEME["primary"]}; color: #FFFFFF; }}

    ::-webkit-scrollbar {{ width: 11px; height: 11px; }}
    ::-webkit-scrollbar-track {{ background: {THEME["bg"]}; }}
    ::-webkit-scrollbar-thumb {{ background: {THEME["border_strong"]}; border-radius: 999px; border: 3px solid {THEME["bg"]}; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {THEME["faint"]}; }}
    * {{ scrollbar-color: {THEME["border_strong"]} {THEME["bg"]}; scrollbar-width: thin; }}

    button:focus-visible, input:focus-visible, textarea:focus-visible, a:focus-visible {{
        outline: 2px solid {THEME["primary"]} !important;
        outline-offset: 2px !important;
        border-radius: 4px;
    }}

    .mono {{
        font-family: 'IBM Plex Mono', monospace;
        font-variant-numeric: tabular-nums;
    }}

    /* ============================= TOP BAR ============================= */
    .topbar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        flex-wrap: wrap;
        padding-bottom: 20px;
        margin-bottom: 40px;
        border-bottom: 1px solid {THEME["border"]};
    }}

    .brand {{
        display: flex;
        align-items: baseline;
        gap: 9px;
    }}

    .brand-word {{
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: 1.15rem;
        letter-spacing: -0.01em;
        color: {THEME["text"]};
    }}

    .live-pill {{
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 6px 12px;
        border-radius: 999px;
        background: {THEME["safe_soft"]};
        color: {THEME["safe"]};
        font-size: 0.8rem;
        font-weight: 600;
    }}

    .live-dot {{
        width: 6px;
        height: 6px;
        border-radius: 999px;
        background: currentColor;
        animation: breathe 2.4s ease-in-out infinite;
    }}

    @keyframes breathe {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.45; transform: scale(0.85); }}
    }}

    /* ============================= HERO ============================= */
    .hero {{ margin-bottom: 36px; }}

    .hero-heading {{
        font-family: 'Fraunces', serif;
        font-weight: 500;
        font-size: 2.75rem;
        line-height: 1.12;
        letter-spacing: -0.02em;
        color: {THEME["text"]};
        max-width: 18ch;
        margin: 0 0 16px 0;
    }}

    .hero-heading em {{
        font-style: italic;
        color: {THEME["primary"]};
    }}

    .hero-sub {{
        font-size: 1.02rem;
        line-height: 1.65;
        color: {THEME["muted"]};
        max-width: 62ch;
        margin-bottom: 22px;
    }}

    .chip-row {{ display: flex; gap: 8px; flex-wrap: wrap; }}

    .chip {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 7px 13px;
        border-radius: 999px;
        background: {THEME["surface_sunken"]};
        border: 1px solid {THEME["border"]};
        font-size: 0.8rem;
        font-weight: 500;
        color: {THEME["muted"]};
    }}

    .chip strong {{ color: {THEME["text"]}; font-weight: 600; }}

    /* ============================= SEGMENTED TABS ============================= */
    div[role="radiogroup"] {{
        display: inline-flex;
        gap: 2px;
        padding: 4px;
        background: {THEME["surface_sunken"]};
        border: 1px solid {THEME["border"]};
        border-radius: 12px;
        margin-bottom: 32px;
    }}

    div[role="radiogroup"] label {{
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 9px 18px;
        cursor: pointer;
        transition: background 0.15s ease, box-shadow 0.15s ease;
    }}

    div[role="radiogroup"] label p {{
        color: {THEME["muted"]} !important;
        font-weight: 600;
        font-size: 0.88rem;
    }}

    div[role="radiogroup"] label > div:first-child {{ display: none !important; }}

    div[role="radiogroup"] label:hover {{ background: rgba(0,0,0,0.03); }}

    div[role="radiogroup"] label:has(input:checked) {{
        background: {THEME["surface"]};
        box-shadow: 0 1px 2px rgba(24,24,27,0.06), 0 1px 1px rgba(24,24,27,0.04);
    }}

    div[role="radiogroup"] label:has(input:checked) p {{ color: {THEME["text"]} !important; }}

    div[role="radiogroup"] label:has(input:focus-visible) {{
        outline: 2px solid {THEME["primary"]};
        outline-offset: 2px;
    }}

    /* ============================= STAT ROW ============================= */
    .stat-row {{
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 20px;
    }}

    .stat {{
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 14px;
        border-radius: 10px;
        background: {THEME["surface"]};
        border: 1px solid {THEME["border"]};
        font-size: 0.83rem;
    }}

    .stat-label {{ color: {THEME["muted"]}; }}
    .stat-value {{ font-weight: 600; color: {THEME["text"]}; }}

    .dot {{ width: 7px; height: 7px; border-radius: 999px; flex-shrink: 0; }}

    /* ============================= SECTION HEADING ============================= */
    .step-heading {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 18px;
    }}

    .step-badge {{
        width: 26px;
        height: 26px;
        min-width: 26px;
        border-radius: 999px;
        background: {THEME["primary_soft"]};
        color: {THEME["primary"]};
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.78rem;
        font-weight: 700;
    }}

    .step-heading h3 {{
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }}

    /* ============================= PANEL ============================= */
    .panel {{
        background: {THEME["surface"]};
        border: 1px solid {THEME["border"]};
        border-radius: 16px;
        padding: 28px 30px;
        box-shadow: 0 1px 2px rgba(24,24,27,0.03);
        margin-bottom: 24px;
    }}

    .panel-title {{
        font-size: 0.78rem;
        font-weight: 600;
        color: {THEME["muted"]};
        margin-bottom: 18px;
        padding-bottom: 14px;
        border-bottom: 1px solid {THEME["border"]};
    }}

    /* ============================= FORM CONTROLS ============================= */
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] {{
        background: {THEME["surface"]} !important;
        color: {THEME["text"]} !important;
        border-radius: 10px !important;
        border: 1px solid {THEME["border_strong"]} !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }}

    .stTextInput input::placeholder {{ color: {THEME["faint"]} !important; }}

    .stTextInput label, .stSelectbox label {{
        font-size: 0.85rem !important;
        font-weight: 500;
        color: {THEME["text"]} !important;
        margin-bottom: 4px !important;
    }}

    div[data-baseweb="base-input"]:focus-within,
    .stTextInput input:focus,
    .stSelectbox div[data-baseweb="select"] > div:focus-within {{
        border-color: {THEME["primary"]} !important;
        box-shadow: 0 0 0 3.5px {THEME["primary_ring"]} !important;
    }}

    /* ============================= BUTTONS ============================= */
    .stButton button {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.68rem 1.1rem !important;
        transition: background 0.15s ease, border-color 0.15s ease, transform 0.05s ease;
    }}

    .stButton button p {{ color: inherit !important; }}

    div[data-testid="column"]:nth-of-type(1) .stButton button,
    .stButton.primary-btn button {{
        background: {THEME["primary"]} !important;
        color: #FFFFFF !important;
        border: 1px solid {THEME["primary"]} !important;
        box-shadow: 0 1px 2px rgba(79,70,229,0.25) !important;
    }}

    .stButton button {{
        background: {THEME["surface"]} !important;
        color: {THEME["text"]} !important;
        border: 1px solid {THEME["border_strong"]} !important;
        box-shadow: 0 1px 2px rgba(24,24,27,0.03) !important;
    }}

    .stButton button:hover {{
        border-color: {THEME["primary"]} !important;
        color: {THEME["primary"]} !important;
    }}

    .stButton button:active {{ transform: translateY(1px); }}

    .stButton button:focus-visible {{
        outline: 2px solid {THEME["primary"]} !important;
        outline-offset: 2px !important;
    }}

    .stButton button:disabled, .stButton button[disabled] {{
        background: {THEME["surface_sunken"]} !important;
        color: {THEME["faint"]} !important;
        border-color: {THEME["border"]} !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
    }}

    .stAlert {{
        border-radius: 12px !important;
        border: 1px solid {THEME["border"]} !important;
        background: {THEME["surface_sunken"]} !important;
        font-size: 0.87rem !important;
    }}

    .stDataFrame, .stJson {{
        border-radius: 12px !important;
        border: 1px solid {THEME["border"]};
        overflow: hidden;
    }}

    hr {{ border-color: {THEME["border"]} !important; }}

    /* ============================= REDACTION FIELD ============================= */
    .redact-field {{
        position: relative;
        border-radius: 10px;
        border: 1px solid {THEME["border"]};
        background: {THEME["surface_sunken"]};
        padding: 14px 16px;
        font-size: 0.95rem;
        color: {THEME["text"]};
        overflow: hidden;
        margin-bottom: 16px;
    }}

    .redact-overlay {{
        position: absolute;
        top: 0; left: 0; height: 100%;
        background: {THEME["text"]};
        transition: width 1s linear;
    }}

    .redact-track {{
        width: 100%;
        height: 6px;
        background: {THEME["surface_sunken"]};
        border-radius: 999px;
        overflow: hidden;
        margin-bottom: 18px;
    }}

    .redact-fill {{
        height: 100%;
        border-radius: 999px;
        transition: width 1s linear, background 0.3s ease;
    }}

    .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.78rem;
    }}

    .status-pill.safe {{ background: {THEME["safe_soft"]}; color: {THEME["safe"]}; }}
    .status-pill.critical {{ background: {THEME["critical_soft"]}; color: {THEME["critical"]}; }}

    .readout-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.87rem;
        color: {THEME["muted"]};
        margin-bottom: 12px;
    }}

    .readout-row strong {{ color: {THEME["text"]}; font-weight: 600; }}

    .helper-note {{
        margin-top: 18px;
        padding-top: 16px;
        border-top: 1px solid {THEME["border"]};
        color: {THEME["muted"]};
        font-size: 0.83rem;
        line-height: 1.55;
    }}

    @media (max-width: 640px) {{
        .block-container {{ padding-top: 1.4rem; }}
        .hero-heading {{ font-size: 2rem; max-width: none; }}
        .panel {{ padding: 22px 20px; }}
        .topbar {{ margin-bottom: 28px; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

if "last_record_id" not in st.session_state:
    st.session_state.last_record_id = None

if "expiry_time" not in st.session_state:
    st.session_state.expiry_time = None


def safe_json_to_df(data):
    if isinstance(data, list) and data:
        return pd.DataFrame(data)
    if isinstance(data, dict):
        return pd.DataFrame([data])
    return pd.DataFrame()


def topbar():
    st.markdown(
        """
        <div class="topbar">
            <div class="brand">
                <span class="brand-word">DataExpiry</span>
            </div>
            <div class="live-pill">
                <span class="live-dot"></span>
                Live demo
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-heading">Cryptographic erasure, <em>on the record</em>.</div>
            <div class="hero-sub">
                Submit sensitive fields through the proxy, attach a retention window, and
                watch the decryption key become permanently unrecoverable at expiry —
                not deleted after the fact, unrecoverable by construction.
            </div>
            <div class="chip-row">
                <span class="chip">Path <strong>Proxy → Vault → Backend</strong></span>
                <span class="chip">Environment <strong>Live demo</strong></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def nav_tabs():
    return st.radio(
        "Navigation",
        ["Protected Intake", "Exposure Test"],
        horizontal=True,
        label_visibility="collapsed",
    )


def stat_row(items):
    cells = "".join(
        f'<div class="stat"><span class="dot" style="background:{color};"></span>'
        f'<span class="stat-label">{label}</span><span class="stat-value">{value}</span></div>'
        for label, value, color in items
    )
    st.markdown(f'<div class="stat-row">{cells}</div>', unsafe_allow_html=True)


def step_heading(number, text):
    st.markdown(
        f"""
        <div class="step-heading">
            <span class="step-badge">{number}</span>
            <h3>{text}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


def protected_intake():
    step_heading(1, "Create a protected record")

    stat_row([
        ("Protection mode", "Active", THEME["safe"]),
        ("Policy engine", "Online", THEME["safe"]),
        ("Vault status", "Healthy", THEME["safe"]),
    ])

    left, right = st.columns([1.25, 0.75], gap="large")

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)

        user_name = st.text_input("Customer name", value="Alice Smith")
        sensitive_data = st.text_input(
            "Sensitive data",
            value="4532-xxxx-xxxx-8891",
            help="Example: card number, ID, SSN, account reference.",
        )

        ttl_options = {
            "15 seconds — Live demo": 15,
            "30 seconds — Standard demo": 30,
            "1 hour — Temporary cache": 3600,
            "24 hours — Daily rotation": 86400,
            "30 days — Compliance retention": 2592000,
            "1 year — Enterprise archival": 31536000,
        }

        selected_ttl = st.selectbox("Retention policy", list(ttl_options.keys()))
        ttl = ttl_options[selected_ttl]

        if st.button("Protect record", use_container_width=True, type="primary"):
            payload = {
                "user_name": user_name,
                "sensitive_data": sensitive_data,
                "ttl_seconds": ttl,
            }
            try:
                with st.spinner("Encrypting and writing to vault…"):
                    res = requests.post(
                        f"{PROXY_URL}/api/records",
                        json=payload,
                        headers=TUNNEL_HEADERS,
                        timeout=20,
                    )
                if res.status_code in (200, 201):
                    body = res.json()
                    st.session_state.last_record_id = body.get("id")
                    st.session_state.expiry_time = time.time() + ttl
                    st.session_state.ttl_total = ttl
                    st.session_state.protected_value = sensitive_data
                    st.success("Record protected. Retention timer started.")
                else:
                    st.error(f"Proxy rejected the record (status {res.status_code}).")
                    with st.expander("Response detail"):
                        st.code(res.text, language=None)
            except requests.RequestException as e:
                st.error("Could not reach the proxy. The vault may be offline or the tunnel expired.")
                with st.expander("Technical detail"):
                    st.code(str(e), language=None)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Policy summary</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="readout-row"><span>Selected TTL</span><strong>{selected_ttl.split(" — ")[0]}</strong></div>
            <div class="readout-row"><span>Encryption path</span><strong>Proxy → Vault</strong></div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.last_record_id:
            st.markdown(
                f'<div class="readout-row"><span>Last record</span>'
                f'<strong class="mono">{st.session_state.last_record_id}</strong></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="color:{THEME["muted"]};font-size:0.85rem;">'
                f'No protected record created in this session yet.</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="helper-note">Use short TTL values during the review so judges '
            'can immediately observe key expiration and retrieval failure.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    render_expiry_panel()


def render_expiry_panel():
    if not st.session_state.last_record_id or not st.session_state.expiry_time:
        return

    step_heading(2, "Watch the key expire")
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    remaining = int(st.session_state.expiry_time - time.time())
    remaining = max(remaining, 0)
    total = st.session_state.get("ttl_total") or max(remaining, 1)
    ratio = max(min(remaining / total, 1), 0)

    if ratio > 0.5:
        tone = THEME["safe"]
    elif ratio > 0.15:
        tone = THEME["warning"]
    else:
        tone = THEME["critical"]

    redacted_pct = (1 - ratio) * 100
    raw_value = st.session_state.get("protected_value", "")

    st.markdown(
        f"""
        <div class="readout-row"><span>Tracked record</span>
            <strong class="mono">{st.session_state.last_record_id}</strong></div>

        <div class="redact-field mono">
            <span style="opacity:0.85;">{raw_value}</span>
            <div class="redact-overlay" style="width:{redacted_pct:.1f}%;"></div>
        </div>

        <div class="redact-track">
            <div class="redact-fill" style="width:{ratio*100:.1f}%; background:{tone};"></div>
        </div>

        <div class="readout-row">
            <span>Key state</span>
            <span>{stamp_html(remaining)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Attempt secure retrieval", use_container_width=True):
        rec_id = st.session_state.last_record_id
        try:
            with st.spinner("Requesting plaintext through proxy…"):
                fetch_res = requests.get(
                    f"{PROXY_URL}/api/records/{rec_id}",
                    headers=TUNNEL_HEADERS,
                    timeout=20,
                )

            if fetch_res.status_code == 200:
                st.success("200 OK — key still active. Plaintext restored through proxy.")
                st.json(fetch_res.json())
            elif fetch_res.status_code == 410:
                st.error("410 Gone — decryption key has already been shredded. This record is unrecoverable.")
                st.json(fetch_res.json())
            else:
                st.warning(f"Unexpected proxy response: {fetch_res.status_code}")
        except requests.RequestException as e:
            st.error("Retrieval request failed. The proxy or tunnel may be unreachable.")
            with st.expander("Technical detail"):
                st.code(str(e), language=None)

    if remaining > 0:
        st.warning(f"Key will expire in {remaining} seconds.")
        if remaining <= 60:
            time.sleep(1)
            st.rerun()
    else:
        st.error("TTL expired — the key has been mathematically shredded from the vault.")

    st.markdown("</div>", unsafe_allow_html=True)


def stamp_html(remaining):
    if remaining > 0:
        return '<span class="status-pill safe">Active</span>'
    return '<span class="status-pill critical">Shredded</span>'


def exposure_test():
    step_heading(1, "See what an attacker would find")

    stat_row([
        ("View type", "Backend exposure", THEME["muted"]),
        ("Expected risk", "High", THEME["critical"]),
        ("Payload readability", "Masked / encrypted", THEME["safe"]),
    ])

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Exposed records — bypasses the vault</div>', unsafe_allow_html=True)

    if st.button("Inspect exposed records", use_container_width=True):
        try:
            with st.spinner("Querying backend directly, bypassing the vault…"):
                db_res = requests.get(
                    f"{BACKEND_URL}/api/records",
                    headers=TUNNEL_HEADERS,
                    timeout=20,
                )
            if db_res.status_code == 200:
                records = db_res.json()
                if records:
                    df = safe_json_to_df(records)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    with st.expander("Raw response"):
                        st.json(records)
                else:
                    st.info("The backend database is currently empty.")
            else:
                st.error(f"Backend returned an unexpected status ({db_res.status_code}).")
        except requests.RequestException as e:
            st.error("Could not reach the backend. It may be offline or the tunnel expired.")
            with st.expander("Technical detail"):
                st.code(str(e), language=None)

    st.markdown("</div>", unsafe_allow_html=True)


topbar()
hero()
page = nav_tabs()

if page == "Protected Intake":
    protected_intake()
elif page == "Exposure Test":
    exposure_test()
