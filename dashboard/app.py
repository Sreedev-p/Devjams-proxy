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

# --- Premium palette: near-black base, warm off-white text, champagne-gold
# accent instead of a bright neon tone. Cards use a subtle translucent
# "glass" surface rather than flat opaque panels. ---
THEME = {
    "bg": "#0A0A0C",
    "bg_glow": "rgba(212, 175, 55, 0.05)",
    "surface": "rgba(255, 255, 255, 0.035)",
    "surface_solid": "#131318",
    "surface_alt": "rgba(255, 255, 255, 0.055)",
    "border": "rgba(255, 255, 255, 0.09)",
    "border_strong": "rgba(212, 175, 55, 0.35)",
    "text": "#F3F1EA",
    "muted": "#9B968C",
    "accent": "#D4AF37",
    "accent_soft": "#C9A961",
    "accent_hover": "#E8C468",
    "accent_text": "#0A0A0C",
    "success": "#8FBF9F",
    "warning": "#D9B36C",
    "danger": "#C97B7B",
}

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

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
            radial-gradient(circle at 12% 0%, {THEME["bg_glow"]}, transparent 40%),
            radial-gradient(circle at 88% 100%, rgba(212, 175, 55, 0.035), transparent 45%),
            {THEME["bg"]};
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

    /* --- Buttons: soft gold, not neon --- */
    .stButton button {{
        background: linear-gradient(180deg, {THEME["accent_hover"]} 0%, {THEME["accent"]} 100%) !important;
        color: {THEME["accent_text"]} !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.65rem 1rem !important;
        box-shadow: 0 8px 20px rgba(212, 175, 55, 0.18);
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

    /* Hide the default circular radio indicator so the label itself
       reads as a selectable tab/pill. */
    div[role="radiogroup"] label > div:first-child {{
        display: none !important;
    }}

    /* Highlight whichever tab is actually selected — soft gold, not a
       loud fill, to stay in the premium register. */
    div[role="radiogroup"] label:has(input:checked) {{
        background: linear-gradient(180deg, rgba(212, 175, 55, 0.22) 0%, rgba(212, 175, 55, 0.14) 100%) !important;
        border-color: {THEME["accent"]} !important;
        box-shadow: 0 6px 18px rgba(212, 175, 55, 0.12);
    }}

    div[role="radiogroup"] label:has(input:checked) p {{
        color: {THEME["accent"]} !important;
        font-weight: 600;
    }}

    .mono {{
        font-family: 'JetBrains Mono', monospace;
    }}

    /* --- Hero: serif display headline over clean sans body, classic
       premium/luxury type pairing --- */
    .hero-card {{
        background: {THEME["surface"]};
        backdrop-filter: blur(20px);
        border: 1px solid {THEME["border"]};
        border-radius: 20px;
        padding: 28px 30px;
        margin-bottom: 1.25rem;
        position: relative;
        overflow: hidden;
    }}

    .hero-card::before {{
        content: "";
        position: absolute;
        top: -40%;
        right: -10%;
        width: 320px;
        height: 320px;
        background: radial-gradient(circle, rgba(212, 175, 55, 0.14), transparent 70%);
        pointer-events: none;
    }}

    .hero-eyebrow {{
        color: {THEME["accent"]};
        font-size: 0.76rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        position: relative;
    }}

    .hero-title {{
        font-family: 'Playfair Display', serif;
        color: {THEME["text"]};
        font-size: 2.4rem;
        font-weight: 600;
        line-height: 1.15;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        position: relative;
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

        # If the key has changed since the last successful verification,
        # the previous verification no longer applies — require re-checking
        # before allowing edits again.
        if admin_key != st.session_state.get("verified_admin_key"):
            st.session_state.admin_key_verified = False

        verify_col, status_col = st.columns([1, 3])
        with verify_col:
            verify_clicked = st.button("Verify Key", use_container_width=True)

        if verify_clicked:
            if not admin_key:
                st.session_state.admin_key_verified = False
                st.error("Enter an Admin API Key first.")
            else:
                try:
                    headers = {"X-Admin-Key": admin_key, **TUNNEL_HEADERS}
                    res = requests.get(
                        f"{PROXY_URL}/api/admin/stats",
                        headers=headers,
                        timeout=20,
                    )
                    if res.status_code == 200:
                        st.session_state.admin_key_verified = True
                        st.session_state.verified_admin_key = admin_key
                    elif res.status_code == 401:
                        st.session_state.admin_key_verified = False
                        st.error("Invalid Admin API Key.")
                    else:
                        st.session_state.admin_key_verified = False
                        st.error(f"Unexpected error verifying key: {res.status_code}")
                except requests.RequestException as e:
                    st.session_state.admin_key_verified = False
                    st.error(f"Could not reach proxy: {e}")

        is_verified = st.session_state.get("admin_key_verified", False)

        with status_col:
            st.write("")
            if is_verified:
                st.success("Key verified — policy editing unlocked.", icon="✅")
            else:
                st.info("Verify your Admin API Key to unlock policy editing.", icon="🔒")

        st.markdown("---")

        if not is_verified:
            st.caption("Fields to encrypt")
            st.write(
                "🔒 Locked. Verify a valid Admin API Key above to view and edit the "
                "encrypted-fields list."
            )
        else:
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
                            # Key may have been rotated/revoked server-side
                            # since verification — re-lock the editor.
                            st.session_state.admin_key_verified = False
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
