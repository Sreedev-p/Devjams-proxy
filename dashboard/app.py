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
BACKEND_URL = "https://thirty-plants-boil.loca.lt"

TUNNEL_HEADERS = {
    "Bypass-Tunnel-Reminder": "true",
    "ngrok-skip-browser-warning": "true",
    "User-Agent": "DataExpiry-App/1.0",
}

THEME = {
    "bg": "#0B1020",
    "bg_soft": "#111827",
    "surface": "#121A2B",
    "surface_alt": "#182338",
    "border": "rgba(148, 163, 184, 0.18)",
    "text": "#E5EEF8",
    "muted": "#B6C2D1",
    "accent": "#1FB8D1",
    "accent_hover": "#18A7BE",
    "accent_text": "#04131A",
    "success": "#34D399",
    "warning": "#FBBF24",
    "danger": "#F87171",
}

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background: linear-gradient(180deg, {THEME["bg"]} 0%, #0F172A 100%);
        color: {THEME["text"]};
    }}

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    [data-testid="stAppViewContainer"] {{
        background:
            radial-gradient(circle at top left, rgba(34, 211, 238, 0.06), transparent 26%),
            linear-gradient(180deg, {THEME["bg"]} 0%, #0F172A 100%);
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}

    h1, h2, h3 {{
        color: {THEME["text"]} !important;
        letter-spacing: -0.02em;
    }}

    p, label, .stMarkdown, .stCaption {{
        color: {THEME["text"]};
    }}

    [data-testid="stMetric"] {{
        background: rgba(18, 26, 43, 0.92);
        border: 1px solid {THEME["border"]};
        border-radius: 16px;
        padding: 14px 16px;
    }}

    [data-testid="stMetricLabel"] {{
        color: {THEME["muted"]} !important;
        font-weight: 600;
        font-size: 0.9rem !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {THEME["text"]};
        font-size: 2.3rem !important;
        line-height: 1.05 !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(18, 26, 43, 0.9);
        border: 1px solid {THEME["border"]};
        border-radius: 18px;
    }}

    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] {{
        background: {THEME["surface_alt"]} !important;
        color: {THEME["text"]} !important;
        border-radius: 12px !important;
        border: 1px solid {THEME["border"]} !important;
    }}

    div[data-baseweb="base-input"]:focus-within,
    .stTextInput input:focus,
    .stSelectbox div[data-baseweb="select"] > div:focus-within {{
        border-color: {THEME["accent"]} !important;
        box-shadow: 0 0 0 1px {THEME["accent"]} !important;
    }}

    .stButton button {{
        background: {THEME["accent"]} !important;
        color: {THEME["accent_text"]} !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.65rem 1rem !important;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.22);
        transition: background 0.15s ease, transform 0.15s ease;
    }}

    .stButton button:hover {{
        background: {THEME["accent_hover"]} !important;
        transform: translateY(-1px);
    }}

    .stAlert {{
        border-radius: 14px !important;
        border: 1px solid {THEME["border"]} !important;
    }}

    .stDataFrame, .stJson {{
        border-radius: 14px !important;
        overflow: hidden;
    }}

    /* --- Top nav (st.radio used as tabs) --- */
    div[role="radiogroup"] {{
        gap: 0.5rem;
        flex-wrap: wrap;
    }}

    div[role="radiogroup"] label {{
        background: rgba(24, 35, 56, 0.9);
        border: 1px solid {THEME["border"]};
        border-radius: 12px;
        padding: 10px 16px;
        cursor: pointer;
        transition: background 0.15s ease, border-color 0.15s ease;
    }}

    div[role="radiogroup"] label:hover {{
        border-color: {THEME["accent"]};
    }}

    div[role="radiogroup"] label p {{
        color: {THEME["text"]} !important;
        font-weight: 600;
    }}

    /* Hide the default circular radio indicator so the label itself
       reads as a selectable tab/pill. */
    div[role="radiogroup"] label > div:first-child {{
        display: none !important;
    }}

    /* Highlight whichever tab is actually selected. */
    div[role="radiogroup"] label:has(input:checked) {{
        background: {THEME["accent"]} !important;
        border-color: {THEME["accent"]} !important;
        box-shadow: 0 6px 18px rgba(31, 184, 209, 0.35);
    }}

    div[role="radiogroup"] label:has(input:checked) p {{
        color: {THEME["accent_text"]} !important;
    }}

    .mono {{
        font-family: 'JetBrains Mono', monospace;
    }}

    .hero-card {{
        background: linear-gradient(180deg, rgba(18,26,43,0.96) 0%, rgba(15,23,42,0.96) 100%);
        border: 1px solid {THEME["border"]};
        border-radius: 20px;
        padding: 22px 24px;
        margin-bottom: 1rem;
    }}

    .hero-eyebrow {{
        color: {THEME["accent"]};
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}

    .hero-title {{
        color: {THEME["text"]};
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.1;
        margin-top: 0.4rem;
        margin-bottom: 0.35rem;
    }}

    .hero-sub {{
        color: {THEME["muted"]};
        font-size: 1rem;
        max-width: 760px;
    }}

    .section-note {{
        color: {THEME["muted"]} !important;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

if "encrypt_fields" not in st.session_state:
    st.session_state.encrypt_fields = ["sensitive_data"]

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
            <div class="hero-title">Zero-Code Cryptographic Erasure</div>
            <div class="hero-sub">
                Protect sensitive data in transit, enforce retention policies,
                and demonstrate irreversible key shredding with a clearer, more product-like interface.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def top_nav():
    return st.radio(
        "Navigation",
        ["Protected Intake", "Exposure Test", "Policy Control", "Security Operations"],
        horizontal=True,
        label_visibility="collapsed",
    )


def render_overview_metrics():
    col1, col2, col3 = st.columns(3)
    col1.metric("Protection Mode", "Active")
    col2.metric("Policy Engine", "Online")
    col3.metric("Vault Status", "Healthy")


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

    c1, c2, c3 = st.columns(3)
    c1.metric("View Type", "Backend Exposure")
    c2.metric("Expected Risk", "High")
    c3.metric("Payload Readability", "Masked / Encrypted")

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


def policy_control():
    st.subheader("Policy Control")
    st.caption("Configure which fields the proxy encrypts before data reaches the target system.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Admin Scope", "Encryption Policy")
    c2.metric("Editable Fields", len(st.session_state.encrypt_fields))
    c3.metric("Mode", "Live Config")

    with st.container(border=True):
        st.markdown('<div class="section-note">Administrative policy settings</div>', unsafe_allow_html=True)

        admin_key = st.text_input("Admin API key", type="password", key="admin_key_input")

        st.write("**Fields to encrypt**")

        fields_to_remove = None
        for idx, value in enumerate(st.session_state.encrypt_fields):
            col_a, col_b = st.columns([6, 1])
            with col_a:
                st.session_state.encrypt_fields[idx] = st.text_input(
                    f"Field {idx + 1}",
                    value=value,
                    key=f"encrypt_field_{idx}",
                    placeholder="e.g. sensitive_data",
                )
            with col_b:
                st.write("")
                st.write("")
                if len(st.session_state.encrypt_fields) > 1:
                    if st.button("Remove", key=f"remove_field_{idx}", use_container_width=True):
                        fields_to_remove = idx

        if fields_to_remove is not None:
            st.session_state.encrypt_fields.pop(fields_to_remove)
            st.rerun()

        left, right = st.columns([1, 1])
        with left:
            if st.button("Add Field", use_container_width=True):
                st.session_state.encrypt_fields.append("")
                st.rerun()

        target_fields = ",".join(
            field.strip() for field in st.session_state.encrypt_fields if field.strip()
        )

        with right:
            if st.button("Enforce Policy", use_container_width=True):
                headers = {"X-Admin-Key": admin_key, **TUNNEL_HEADERS}
                payload = {"fields": target_fields}
                try:
                    res = requests.post(
                        f"{PROXY_URL}/api/admin/config",
                        json=payload,
                        headers=headers,
                        timeout=20,
                    )
                    if res.status_code in (200, 201):
                        st.success(f"Active fields: {res.json().get('active_fields')}")
                    elif res.status_code == 401:
                        st.error("Invalid admin key.")
                    else:
                        st.error(f"Unexpected error: {res.status_code} — {res.text}")
                except requests.RequestException as e:
                    st.error(f"Could not reach proxy: {e}")

    with st.container(border=True):
        st.markdown('<div class="section-note">Current policy</div>', unsafe_allow_html=True)
        if st.button("Refresh Active Policy", use_container_width=True):
            try:
                cfg_res = requests.get(
                    f"{PROXY_URL}/api/admin/config",
                    headers=TUNNEL_HEADERS,
                    timeout=20,
                )
                if cfg_res.status_code == 200:
                    st.info(f"Currently encrypting: {cfg_res.json().get('active_fields')}")
                else:
                    st.warning(f"Could not fetch config: {cfg_res.status_code}")
            except requests.RequestException as e:
                st.warning(f"Proxy unreachable: {e}")


def security_operations():
    st.subheader("Security Operations")
    st.caption("Review telemetry, event volume, and the immutable cryptographic audit trail.")

    soc_key = st.text_input("Admin API key", type="password", key="soc_admin_key")

    if st.button("Fetch Live Telemetry", use_container_width=True):
        try:
            headers = {"X-Admin-Key": soc_key, **TUNNEL_HEADERS}
            res = requests.get(
                f"{PROXY_URL}/api/admin/logs",
                headers=headers,
                timeout=20,
            )

            if res.status_code == 200:
                data = res.json()
                summary = data.get("summary", {})
                logs = data.get("logs", [])

                col1, col2, col3 = st.columns(3)
                col1.metric("Active Encrypted Keys", summary.get("active_keys", 0))
                col2.metric("Shredded Keys", summary.get("shredded_keys", 0))
                col3.metric("Decryption Attempts", summary.get("decryption_attempts", 0))

                st.markdown("### Event Ledger")
                if logs:
                    df = safe_json_to_df(logs)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    with st.expander("Raw event payload"):
                        st.json(logs)
                else:
                    st.info("No cryptographic events logged yet.")
            elif res.status_code == 401:
                st.error("Invalid admin key.")
            else:
                st.error(f"Error fetching logs: {res.status_code}")
        except requests.RequestException as e:
            st.error(f"Cannot connect to proxy: {e}")


hero()
page = top_nav()

st.markdown("")

if page == "Protected Intake":
    protected_intake()
elif page == "Exposure Test":
    exposure_test()
elif page == "Policy Control":
    policy_control()
else:
    security_operations()
