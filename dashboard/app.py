import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="DataExpiry",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PROXY_URL = "https://latrine-primal-retired.ngrok-free.dev"
BACKEND_URL = "https://shaky-jokes-lick.loca.lt"

TUNNEL_HEADERS = {
    "Bypass-Tunnel-Reminder": "true",
    "ngrok-skip-browser-warning": "true",
    "User-Agent": "DataExpiry-App/1.0",
}

THEME = {
    "bg": "#070A10",
    "bg_glow": "rgba(59, 130, 246, 0.07)",
    "surface": "rgba(255, 255, 255, 0.035)",
    "surface_solid": "#0E131C",
    "surface_alt": "rgba(255, 255, 255, 0.055)",
    "border": "rgba(148, 163, 184, 0.14)",
    "border_strong": "rgba(59, 130, 246, 0.45)",
    "text": "#E7ECF3",
    "muted": "#8B96A5",
    "accent": "#3B82F6",
    "accent_soft": "#5B9DFF",
    "accent_hover": "#5B9DFF",
    "accent_text": "#04070C",
    "success": "#34D399",
    "warning": "#F5C56C",
    "danger": "#F1706E",
}

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background: {THEME["bg"]};
        color: {THEME["text"]};
    }}

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    [data-testid="stAppViewContainer"] {{
        background:
            radial-gradient(circle at 10% -5%, {THEME["bg_glow"]}, transparent 42%),
            radial-gradient(circle at 90% 105%, rgba(59, 130, 246, 0.05), transparent 46%),
            radial-gradient(circle, rgba(148, 163, 184, 0.05) 1px, transparent 1px),
            {THEME["bg"]};
        background-size: auto, auto, 26px 26px, auto;
    }}

    .block-container {{
        padding-top: 2.5rem;
        padding-bottom: 2.5rem;
        max-width: 1200px;
    }}

    h1, h2, h3 {{
        color: {THEME["text"]} !important;
        letter-spacing: -0.02em;
    }}

    p, label, .stMarkdown, .stCaption {{
        color: {THEME["text"]};
    }}

    /* --- Metrics --- */
    [data-testid="stMetric"] {{
        background: {THEME["surface"]};
        backdrop-filter: blur(18px);
        border: 1px solid {THEME["border"]};
        border-radius: 14px;
        padding: 16px 18px;
    }}

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] * {{
        color: {THEME["muted"]} !important;
        font-weight: 500 !important;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] * {{
        color: {THEME["text"]} !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        overflow-wrap: break-word !important;
    }}

    /* --- Card containers --- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {THEME["surface"]};
        backdrop-filter: blur(18px);
        border: 1px solid {THEME["border"]};
        border-radius: 18px;
    }}

    /* --- Inputs --- */
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] {{
        background: {THEME["surface_alt"]} !important;
        color: {THEME["text"]} !important;
        border-radius: 10px !important;
        border: 1px solid {THEME["border"]} !important;
    }}

    .stTextInput input::placeholder {{
        color: {THEME["muted"]} !important;
    }}

    div[data-baseweb="base-input"]:focus-within,
    .stTextInput input:focus,
    .stSelectbox div[data-baseweb="select"] > div:focus-within {{
        border-color: {THEME["accent"]} !important;
        box-shadow: 0 0 0 1px {THEME["accent"]} !important;
    }}

    /* --- Buttons --- */
    .stButton button {{
        background: linear-gradient(180deg, {THEME["accent_soft"]} 0%, {THEME["accent"]} 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.65rem 1rem !important;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.20);
        transition: filter 0.15s ease, transform 0.15s ease;
    }}

    .stButton button:hover {{
        filter: brightness(1.06);
        transform: translateY(-1px);
    }}

    .stButton button:active {{
        transform: translateY(0);
        filter: brightness(0.96);
    }}

    .stAlert {{
        background: {THEME["surface"]} !important;
        backdrop-filter: blur(14px);
        border-radius: 12px !important;
        border: 1px solid {THEME["border"]} !important;
    }}

    .stDataFrame, .stJson {{
        border-radius: 12px !important;
        overflow: hidden;
        border: 1px solid {THEME["border"]};
    }}

    /* --- Top nav (st.radio used as tabs) --- */
    div[role="radiogroup"] {{
        gap: 0.5rem;
        flex-wrap: wrap;
    }}

    div[role="radiogroup"] label {{
        background: {THEME["surface"]};
        backdrop-filter: blur(14px);
        border: 1px solid {THEME["border"]};
        border-radius: 10px;
        padding: 10px 18px;
        cursor: pointer;
        transition: background 0.15s ease, border-color 0.15s ease;
    }}

    div[role="radiogroup"] label:hover {{
        border-color: {THEME["border_strong"]};
    }}

    div[role="radiogroup"] label p {{
        color: {THEME["text"]} !important;
        font-weight: 500;
        font-size: 0.92rem;
    }}

    div[role="radiogroup"] label > div:first-child {{
        display: none !important;
    }}

    div[role="radiogroup"] label:has(input:checked) {{
        background: linear-gradient(180deg, rgba(59, 130, 246, 0.22) 0%, rgba(59, 130, 246, 0.14) 100%) !important;
        border-color: {THEME["accent"]} !important;
        box-shadow: 0 6px 18px rgba(59, 130, 246, 0.16);
    }}

    div[role="radiogroup"] label:has(input:checked) p {{
        color: {THEME["accent_soft"]} !important;
        font-weight: 600;
    }}

    .mono {{
        font-family: 'JetBrains Mono', monospace;
    }}

    /* --- Hero --- */
    .hero-card {{
        background: {THEME["surface"]};
        backdrop-filter: blur(20px);
        border: 1px solid {THEME["border"]};
        border-radius: 20px;
        padding: 28px 30px 40px 30px;
        margin-bottom: 2.5rem;
        position: relative;
        overflow: visible;
    }}

    .hero-card::before {{
        content: "";
        position: absolute;
        top: -40%;
        right: -10%;
        width: 320px;
        height: 320px;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.16), transparent 70%);
        pointer-events: none;
    }}

    .hero-eyebrow {{
        color: {THEME["accent_soft"]};
        font-size: 0.76rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-family: 'JetBrains Mono', monospace;
        position: relative;
    }}

    .hero-title {{
        font-family: 'Space Grotesk', sans-serif;
        color: {THEME["text"]};
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1.15;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        position: relative;
    }}

    .hero-title .accent-word {{
        color: {THEME["accent_soft"]};
        font-style: italic;
        font-weight: 600;
    }}

    .status-chip {{
        position: absolute;
        bottom: -16px;
        left: 30px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: {THEME["surface_solid"]};
        border: 1px solid {THEME["border_strong"]};
        border-radius: 999px;
        padding: 8px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        font-weight: 500;
        color: {THEME["text"]};
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.45);
        z-index: 2;
    }}

    .status-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: {THEME["success"]};
        box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.6);
        animation: pulse-dot 2s infinite;
    }}

    @keyframes pulse-dot {{
        0% {{ box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.55); }}
        70% {{ box-shadow: 0 0 0 8px rgba(52, 211, 153, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }}
    }}

    .stat-strip {{
        display: flex;
        align-items: stretch;
        gap: 0;
        border: 1px solid {THEME["border"]};
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 1.5rem;
    }}

    .stat-strip-item {{
        flex: 1;
        padding: 14px 20px;
        border-right: 1px solid {THEME["border"]};
    }}

    .stat-strip-item:last-child {{
        border-right: none;
    }}

    .stat-strip-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {THEME["muted"]};
        margin-bottom: 4px;
    }}

    .stat-strip-value {{
        font-size: 1.15rem;
        font-weight: 600;
        color: {THEME["text"]};
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .hero-sub {{
        color: {THEME["muted"]};
        font-size: 1rem;
        max-width: 760px;
        position: relative;
        line-height: 1.6;
    }}

    .section-note {{
        color: {THEME["muted"]} !important;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.8rem;
    }}

    hr {{
        border-color: {THEME["border"]} !important;
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


def hero():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-eyebrow">DataExpiry Platform</div>
            <div class="hero-title">Zero-Code <span class="accent-word">Cryptographic</span> Erasure</div>
            <div class="hero-sub">
                Protect sensitive data in transit, enforce retention policies,
                and demonstrate irreversible key shredding with a clearer, more product-like interface.
            </div>
            <div class="status-chip">
                <span class="status-dot"></span>
                Reaper daemon active — scanning every 2s
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def top_nav():
    # Admin tabs removed for production isolation
    return st.radio(
        "Navigation",
        ["Protected Intake", "Exposure Test"],
        horizontal=True,
        label_visibility="collapsed",
    )


def stat_strip(items):
    cells = "".join(
        f'<div class="stat-strip-item">'
        f'<div class="stat-strip-label">{label}</div>'
        f'<div class="stat-strip-value">{value}</div>'
        f'</div>'
        for label, value in items
    )
    st.markdown(f'<div class="stat-strip">{cells}</div>', unsafe_allow_html=True)


def render_overview_metrics():
    stat_strip([
        ("Protection Mode", '<span class="status-dot"></span>Active'),
        ("Policy Engine", "Online"),
        ("Vault Status", "Healthy"),
    ])


def protected_intake():
    st.subheader("Protected Intake")
    st.caption("Submit sensitive information through the proxy and attach a retention policy.")

    render_overview_metrics()

    left, right = st.columns([1.2, 0.8], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<div class="section-note">Create protected record</div>', unsafe_allow_html=True)

            user_name = st.text_input("Customer name", value="Alice Smith")
            sensitive_data = st.text_input(
                "Sensitive data",
                value="4532-xxxx-xxxx-8891",
                help="Example: card number, ID, SSN, account reference.",
            )

            ttl_options = {
                "15 Seconds — Live demo": 15,
                "30 Seconds — Standard demo": 30,
                "1 Hour — Temporary cache": 3600,
                "24 Hours — Daily rotation": 86400,
                "30 Days — Compliance retention": 2592000,
                "1 Year — Enterprise archival": 31536000,
            }

            selected_ttl = st.selectbox("Retention policy", list(ttl_options.keys()))
            ttl = ttl_options[selected_ttl]

            if st.button("Protect Record", use_container_width=True):
                payload = {
                    "user_name": user_name,
                    "sensitive_data": sensitive_data,
                    "ttl_seconds": ttl,
                }
                try:
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
                        st.success("Record protected successfully and retention timer started.")
                    else:
                        st.error(f"Proxy error: {res.status_code} — {res.text}")
                except requests.RequestException as e:
                    st.error(f"Could not connect to proxy: {e}")

    with right:
        with st.container(border=True):
            st.markdown('<div class="section-note">Policy summary</div>', unsafe_allow_html=True)
            st.metric("Selected TTL", selected_ttl.split(" — ")[0])
            st.metric("Encryption path", "Proxy → Vault → Backend")
            if st.session_state.last_record_id:
                st.markdown(
                    f"**Last record ID:** <span class='mono'>{st.session_state.last_record_id}</span>",
                    unsafe_allow_html=True,
                )
            else:
                st.info("No protected record created in this session yet.")

            st.markdown("---")
            st.write(
                "Use short TTL values during the review so judges can immediately observe key expiration and retrieval failure."
            )

    render_expiry_panel()


def render_expiry_panel():
    if not st.session_state.last_record_id or not st.session_state.expiry_time:
        return

    with st.container(border=True):
        st.subheader("Cryptographic Shredding Test")

        remaining = int(st.session_state.expiry_time - time.time())

        a, b, c = st.columns(3)
        a.metric("Tracked Record", st.session_state.last_record_id)
        b.metric("Seconds Remaining", max(remaining, 0))
        c.metric("Vault Key State", "Active" if remaining > 0 else "Shredded")

        if st.button("Attempt Secure Retrieval", use_container_width=True):
            rec_id = st.session_state.last_record_id
            try:
                fetch_res = requests.get(
                    f"{PROXY_URL}/api/records/{rec_id}",
                    headers=TUNNEL_HEADERS,
                    timeout=20,
                )

                if fetch_res.status_code == 200:
                    st.success("200 OK — key still active. Plaintext restored through proxy.")
                    st.json(fetch_res.json())
                elif fetch_res.status_code == 410:
                    st.error("410 Gone — decryption key has already been shredded.")
                    st.json(fetch_res.json())
                else:
                    st.warning(f"Unexpected proxy response: {fetch_res.status_code}")
            except requests.RequestException as e:
                st.error(f"Retrieval failed: {e}")

        if remaining > 0:
            st.warning(f"Key will expire in {remaining} seconds.")
            if remaining <= 60:
                time.sleep(1)
                st.rerun()
        else:
            st.error("TTL expired — the key has been mathematically shredded from the vault.")


def exposure_test():
    st.subheader("Exposure Test")
    st.caption("Inspect what the target database reveals without proxy-side decryption.")

    stat_strip([
        ("View Type", "Backend Exposure"),
        ("Expected Risk", '<span class="status-dot" style="background:{danger}"></span>High'.replace("{danger}", THEME["danger"])),
        ("Payload Readability", "Masked / Encrypted"),
    ])

    with st.container(border=True):
        st.markdown('<div class="section-note">Exposed records</div>', unsafe_allow_html=True)

        if st.button("Inspect Exposed Records", use_container_width=True):
            try:
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
                    st.error(f"Failed to read backend database: {db_res.status_code}")
            except requests.RequestException as e:
                st.error(f"Backend connection failed: {e}")


hero()
page = top_nav()

st.markdown("")

if page == "Protected Intake":
    protected_intake()
elif page == "Exposure Test":
    exposure_test()
