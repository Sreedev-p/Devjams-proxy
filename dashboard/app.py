import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="DataExpiry",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PROXY_URL = "https://latrine-primal-retired.ngrok-free.dev"
BACKEND_URL = "https://rare-bobcats-work.loca.lt"

TUNNEL_HEADERS = {
    "Bypass-Tunnel-Reminder": "true",
    "ngrok-skip-browser-warning": "true",
    "User-Agent": "DataExpiry-App/1.0",
    "Accept": "application/json, text/plain, */*",
}

THEME = {
    "bg": "#0A0B0D",
    "surface": "#101114",
    "surface_alt": "#16181C",
    "border": "#2A2D33",
    "border_strong": "#3A3E46",
    "text": "#EDEFF1",
    "muted": "#888D96",
    "safe": "#33D17A",
    "critical": "#FF4D4F",
    "warn": "#E8B339",
    "ink_on_light": "#0A0B0D",
}

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

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
        background: {THEME["bg"]};
    }}

    .block-container {{
        padding-top: 1.75rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }}

    h1, h2, h3 {{
        color: {THEME["text"]} !important;
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: -0.01em;
        font-weight: 600;
    }}

    h2 {{ font-size: 1.05rem !important; text-transform: uppercase; letter-spacing: 0.06em !important; }}
    h3 {{ font-size: 0.95rem !important; }}

    p, label, .stMarkdown, .stCaption {{
        color: {THEME["text"]};
    }}

    ::selection {{ background: {THEME["safe"]}; color: {THEME["ink_on_light"]}; }}

    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: {THEME["bg"]}; }}
    ::-webkit-scrollbar-thumb {{ background: {THEME["border_strong"]}; border-radius: 0; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {THEME["muted"]}; }}
    * {{ scrollbar-color: {THEME["border_strong"]} {THEME["bg"]}; scrollbar-width: thin; }}

    button:focus-visible, input:focus-visible, textarea:focus-visible, a:focus-visible {{
        outline: 2px solid {THEME["text"]} !important;
        outline-offset: 2px !important;
    }}

    .mono {{
        font-family: 'JetBrains Mono', monospace;
    }}

    .rail {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        flex-wrap: wrap;
        padding: 0 0 14px 0;
        border-bottom: 1px solid {THEME["border"]};
        margin-bottom: 28px;
    }}

    .rail-brand {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    .rail-mark {{
        width: 22px;
        height: 22px;
        border: 1.5px solid {THEME["text"]};
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.62rem;
        color: {THEME["text"]};
    }}

    .rail-word {{
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 0.92rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: {THEME["text"]};
    }}

    .rail-status {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.04em;
        color: {THEME["muted"]};
        text-transform: uppercase;
    }}

    .rail-status .glyph {{
        width: 7px;
        height: 7px;
        animation: hard-blink 1.6s steps(1, end) infinite;
    }}

    @keyframes hard-blink {{
        0%, 49% {{ opacity: 1; }}
        50%, 100% {{ opacity: 0.25; }}
    }}

    .titleblock {{
        position: relative;
        border: 1px solid {THEME["border"]};
        padding: 30px 34px;
        margin-bottom: 30px;
    }}

    .titleblock::before, .titleblock::after,
    .titleblock .tick-br, .titleblock .tick-bl {{
        content: "";
        position: absolute;
        width: 14px;
        height: 14px;
        border: 1.5px solid {THEME["text"]};
    }}

    .titleblock::before {{ top: -1px; left: -1px; border-right: none; border-bottom: none; }}
    .titleblock::after {{ top: -1px; right: -1px; border-left: none; border-bottom: none; }}
    .titleblock .tick-bl {{ bottom: -1px; left: -1px; border-right: none; border-top: none; }}
    .titleblock .tick-br {{ bottom: -1px; right: -1px; border-left: none; border-top: none; }}

    .titleblock-heading {{
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 2.15rem;
        letter-spacing: -0.01em;
        line-height: 1.12;
        color: {THEME["text"]};
        margin: 0 0 12px 0;
        max-width: 20ch;
    }}

    .titleblock-sub {{
        color: {THEME["muted"]};
        font-size: 0.98rem;
        line-height: 1.6;
        max-width: 62ch;
        margin-bottom: 20px;
    }}

    .titleblock-meta {{
        display: flex;
        gap: 28px;
        flex-wrap: wrap;
        padding-top: 16px;
        border-top: 1px solid {THEME["border"]};
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.03em;
        color: {THEME["muted"]};
        text-transform: uppercase;
    }}

    .titleblock-meta strong {{
        color: {THEME["text"]};
        font-weight: 600;
    }}

    div[role="radiogroup"] {{
        gap: 0;
        border-bottom: 1px solid {THEME["border"]};
        margin-bottom: 26px;
    }}

    div[role="radiogroup"] label {{
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        border-radius: 0;
        padding: 10px 4px;
        margin-right: 28px;
        cursor: pointer;
        transition: border-color 0.12s ease;
    }}

    div[role="radiogroup"] label p {{
        color: {THEME["muted"]} !important;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        font-size: 0.8rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}

    div[role="radiogroup"] label > div:first-child {{
        display: none !important;
    }}

    div[role="radiogroup"] label:hover p {{
        color: {THEME["text"]} !important;
    }}

    div[role="radiogroup"] label:has(input:checked) {{
        border-bottom-color: {THEME["text"]};
    }}

    div[role="radiogroup"] label:has(input:checked) p {{
        color: {THEME["text"]} !important;
    }}

    div[role="radiogroup"] label:has(input:focus-visible) {{
        outline: 2px solid {THEME["text"]};
        outline-offset: 2px;
    }}

    .ledger {{
        display: flex;
        border: 1px solid {THEME["border"]};
        margin-bottom: 24px;
    }}

    .ledger-cell {{
        flex: 1;
        padding: 12px 18px;
        border-right: 1px solid {THEME["border"]};
    }}

    .ledger-cell:last-child {{ border-right: none; }}

    .ledger-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.66rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: {THEME["muted"]};
        margin-bottom: 5px;
    }}

    .ledger-value {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.92rem;
        font-weight: 600;
        color: {THEME["text"]};
        display: flex;
        align-items: center;
        gap: 7px;
        flex-wrap: wrap;
    }}

    .glyph-sq {{
        width: 7px;
        height: 7px;
        display: inline-block;
        flex-shrink: 0;
    }}

    .panel {{
        border: 1px solid {THEME["border"]};
        padding: 22px 24px;
        margin-bottom: 20px;
    }}

    .panel-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: {THEME["muted"]};
        padding-bottom: 10px;
        margin-bottom: 16px;
        border-bottom: 1px solid {THEME["border"]};
    }}

    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] {{
        background: {THEME["surface"]} !important;
        color: {THEME["text"]} !important;
        border-radius: 0 !important;
        border: 1px solid {THEME["border"]} !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88rem !important;
    }}

    .stTextInput input::placeholder {{ color: {THEME["muted"]} !important; }}

    .stTextInput label, .stSelectbox label, .stCheckbox label {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: {THEME["muted"]} !important;
    }}

    div[data-baseweb="base-input"]:focus-within,
    .stTextInput input:focus,
    .stSelectbox div[data-baseweb="select"] > div:focus-within {{
        border-color: {THEME["text"]} !important;
        box-shadow: inset 0 -2px 0 0 {THEME["text"]} !important;
    }}

    .stButton button {{
        background: transparent !important;
        color: {THEME["text"]} !important;
        border: 1px solid {THEME["text"]} !important;
        border-radius: 0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 0.7rem 1rem !important;
        box-shadow: none !important;
        transition: background 0.1s steps(1, end), color 0.1s steps(1, end);
    }}

    .stButton button p {{
        color: inherit !important;
    }}

    .stButton button:hover {{
        background: {THEME["text"]} !important;
        color: {THEME["ink_on_light"]} !important;
    }}

    .stButton button:active {{
        background: {THEME["muted"]} !important;
    }}

    .stButton button:focus-visible {{
        outline: 2px solid {THEME["safe"]} !important;
        outline-offset: 2px !important;
    }}

    .stAlert {{
        border-radius: 0 !important;
        border: 1px solid {THEME["border"]} !important;
        background: {THEME["surface"]} !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem !important;
    }}

    .stDataFrame, .stJson {{
        border-radius: 0 !important;
        border: 1px solid {THEME["border"]};
    }}

    .redact-field {{
        position: relative;
        border: 1px solid {THEME["border"]};
        background: {THEME["surface"]};
        padding: 14px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem;
        color: {THEME["text"]};
        overflow: hidden;
        margin-bottom: 14px;
        letter-spacing: 0.02em;
    }}

    .redact-overlay {{
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        background: #000000;
        transition: width 1s linear;
    }}

    .redact-track {{
        width: 100%;
        height: 3px;
        background: {THEME["surface_alt"]};
        border: 1px solid {THEME["border"]};
        overflow: hidden;
        margin-bottom: 16px;
    }}

    .redact-fill {{
        height: 100%;
        transition: width 1s linear, background 0.3s ease;
    }}

    .stamp {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.78rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 7px 14px;
        border: 2px solid currentColor;
    }}

    .stamp-safe {{ color: {THEME["safe"]}; }}
    .stamp-critical {{ color: {THEME["critical"]}; transform: rotate(-1.5deg); }}

    .readout-row {{
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        gap: 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: {THEME["muted"]};
        margin-bottom: 8px;
        flex-wrap: wrap;
    }}

    .readout-row strong {{
        color: {THEME["text"]};
        font-size: 1rem;
        font-weight: 700;
    }}

    @media (max-width: 640px) {{
        .block-container {{ padding-top: 1.2rem; }}
        .titleblock {{ padding: 24px 20px; }}
        .titleblock-heading {{ font-size: 1.6rem; max-width: none; }}
        .ledger {{ flex-direction: column; }}
        .ledger-cell {{ border-right: none; border-bottom: 1px solid {THEME["border"]}; }}
        .ledger-cell:last-child {{ border-bottom: none; }}
        .rail {{ padding-bottom: 12px; }}
        div[role="radiogroup"] label {{ margin-right: 16px; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

if "last_record_id" not in st.session_state:
    st.session_state.last_record_id = None
if "expiry_time" not in st.session_state:
    st.session_state.expiry_time = None
if "ttl_total" not in st.session_state:
    st.session_state.ttl_total = None
if "protected_value" not in st.session_state:
    st.session_state.protected_value = None


def safe_json_to_df(data):
    if isinstance(data, list):
        return pd.DataFrame(data)
    if isinstance(data, dict):
        if isinstance(data.get("records"), list):
            return pd.DataFrame(data["records"])
        return pd.DataFrame([data])
    return pd.DataFrame()


def fetch_response(url, method="GET", json_body=None, timeout=12):
    try:
        response = requests.request(
            method=method,
            url=url,
            json=json_body,
            headers=TUNNEL_HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )
        content_type = response.headers.get("Content-Type", "")
        text_preview = response.text[:500] if response.text else ""

        parsed_json = None
        is_json = "application/json" in content_type.lower()
        if is_json:
            try:
                parsed_json = response.json()
            except ValueError:
                parsed_json = None

        preview_lower = text_preview.lower()
        looks_like_tunnel_page = (
            "<html" in preview_lower
            or "tunnel reminder" in preview_lower
            or ("ngrok" in preview_lower and "visit site" in preview_lower)
            or "localtunnel" in preview_lower
        )

        return {
            "ok": response.ok,
            "reachable": True,
            "status_code": response.status_code,
            "content_type": content_type,
            "json": parsed_json,
            "text_preview": text_preview,
            "looks_like_tunnel_page": looks_like_tunnel_page,
            "error": None,
        }
    except requests.RequestException as exc:
        return {
            "ok": False,
            "reachable": False,
            "status_code": None,
            "content_type": None,
            "json": None,
            "text_preview": "",
            "looks_like_tunnel_page": False,
            "error": str(exc),
        }


@st.cache_data(ttl=5, show_spinner=False)
def fetch_endpoint_status(url):
    return fetch_response(url, timeout=8)


@st.cache_data(ttl=5, show_spinner=False)
def fetch_endpoint_records(url):
    result = fetch_response(url, timeout=15)
    if not result["reachable"]:
        raise requests.RequestException(result["error"])
    if result["looks_like_tunnel_page"]:
        raise requests.RequestException("Tunnel warning page returned instead of API JSON.")
    if not result["ok"]:
        raise requests.RequestException(f"HTTP {result['status_code']}: {result['text_preview']}")
    if result["json"] is None:
        raise requests.RequestException(
            f"Expected JSON but received {result['content_type'] or 'unknown content'}."
        )
    return result["json"]


def clear_live_cache():
    fetch_endpoint_status.clear()
    fetch_endpoint_records.clear()


def classify_status(result):
    if not result["reachable"]:
        return ("Offline", THEME["critical"], result["error"] or "Unreachable")
    if result["looks_like_tunnel_page"]:
        return ("Tunnel Gate", THEME["warn"], "Tunnel interstitial/reminder page returned")
    if result["ok"]:
        if result["json"] is not None:
            return ("Live", THEME["safe"], f"HTTP {result['status_code']} JSON")
        return ("Reachable", THEME["warn"], f"HTTP {result['status_code']} non-JSON")
    return ("Error", THEME["critical"], f"HTTP {result['status_code']}")


proxy_records_url = f"{PROXY_URL}/api/records"
backend_records_url = f"{BACKEND_URL}/api/records"

proxy_status = fetch_endpoint_status(proxy_records_url)
backend_status = fetch_endpoint_status(backend_records_url)


def rail(proxy_status, backend_status):
    proxy_label, _, _ = classify_status(proxy_status)
    backend_label, _, _ = classify_status(backend_status)

    if proxy_status["reachable"] and backend_status["reachable"] and not proxy_status["looks_like_tunnel_page"] and not backend_status["looks_like_tunnel_page"]:
        status_text = "LIVE · proxy + backend reachable"
        status_color = THEME["safe"]
    elif proxy_status["reachable"] or backend_status["reachable"]:
        status_text = f"PARTIAL · proxy {proxy_label.lower()} / backend {backend_label.lower()}"
        status_color = THEME["warn"]
    else:
        status_text = "OFFLINE · services unreachable"
        status_color = THEME["critical"]

    st.markdown(
        f"""
        <div class="rail">
            <div class="rail-brand">
                <span class="rail-mark">DX</span>
                <span class="rail-word">DataExpiry</span>
            </div>
            <div class="rail-status">
                <span class="glyph" style="background:{status_color};"></span>
                {status_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def titleblock():
    st.markdown(
        """
        <div class="titleblock">
            <div class="tick-bl"></div>
            <div class="tick-br"></div>
            <div class="titleblock-heading">Cryptographic erasure, on the record.</div>
            <div class="titleblock-sub">
                Submit sensitive fields through the proxy, attach a retention window,
                and watch the decryption key go permanently unrecoverable at expiry —
                not deleted after the fact, unrecoverable by construction.
            </div>
            <div class="titleblock-meta">
                <span>DATA: <strong>LIVE API RESPONSES</strong></span>
                <span>WRITE PATH: <strong>PROXY API</strong></span>
                <span>READ PATH: <strong>BACKEND API</strong></span>
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


def ledger(items):
    cells = "".join(
        f'<div class="ledger-cell">'
        f'<div class="ledger-label">{label}</div>'
        f'<div class="ledger-value">{value}</div>'
        f'</div>'
        for label, value in items
    )
    st.markdown(f'<div class="ledger">{cells}</div>', unsafe_allow_html=True)


def glyph(color):
    return f'<span class="glyph-sq" style="background:{color};"></span>'


def stamp_html(remaining):
    if remaining > 0:
        return '<span class="stamp stamp-safe">Active</span>'
    return '<span class="stamp stamp-critical">Shredded</span>'


def system_ledger(proxy_status, backend_status):
    proxy_label, proxy_color, proxy_detail = classify_status(proxy_status)
    backend_label, backend_color, backend_detail = classify_status(backend_status)

    ledger([
        ("Proxy API", f"{glyph(proxy_color)}{proxy_label} · {proxy_detail}"),
        ("Backend API", f"{glyph(backend_color)}{backend_label} · {backend_detail}"),
        ("Checked", time.strftime("%H:%M:%S")),
    ])


def render_expiry_panel():
    if not st.session_state.last_record_id or not st.session_state.expiry_time:
        return

    st.markdown(
        '<div class="panel-label" style="margin-top:24px;">02 · Cryptographic shredding test</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    remaining = max(int(st.session_state.expiry_time - time.time()), 0)
    total = st.session_state.ttl_total or max(remaining, 1)
    ratio = max(min(remaining / total, 1), 0)

    if ratio > 0.5:
        tone = THEME["safe"]
    elif ratio > 0.15:
        tone = THEME["warn"]
    else:
        tone = THEME["critical"]

    redacted_pct = (1 - ratio) * 100
    raw_value = st.session_state.protected_value or ""

    st.markdown(
        f"""
        <div class="readout-row"><span>Tracked record</span>
            <strong class="mono">{st.session_state.last_record_id}</strong></div>

        <div class="redact-field">
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

    if st.button("Attempt Secure Retrieval", use_container_width=True):
        fetch_result = fetch_response(f"{PROXY_URL}/api/records/{st.session_state.last_record_id}", timeout=12)

        if not fetch_result["reachable"]:
            st.error("Retrieval request failed. The proxy may be unreachable.")
            st.code(fetch_result["error"], language=None)
        elif fetch_result["looks_like_tunnel_page"]:
            st.error("Proxy tunnel returned an interstitial page instead of the API response.")
            st.code(fetch_result["text_preview"], language=None)
        elif fetch_result["status_code"] == 200:
            st.success("200 OK — key still active. Plaintext restored through proxy.")
            if fetch_result["json"] is not None:
                st.json(fetch_result["json"])
            else:
                st.code(fetch_result["text_preview"], language=None)
        elif fetch_result["status_code"] == 410:
            st.error("410 Gone — decryption key has been shredded. This record is unrecoverable.")
            if fetch_result["json"] is not None:
                st.json(fetch_result["json"])
            else:
                st.code(fetch_result["text_preview"], language=None)
        else:
            st.warning(f"Unexpected proxy response: {fetch_result['status_code']}")
            if fetch_result["json"] is not None:
                st.json(fetch_result["json"])
            else:
                st.code(fetch_result["text_preview"], language=None)

    if remaining > 0:
        st.warning(f"Key will expire in {remaining} seconds.")
    else:
        st.error("TTL expired — the key has been mathematically shredded from the vault.")

    st.markdown("</div>", unsafe_allow_html=True)


def live_records_panel(default_source="Proxy records", key_suffix="main"):
    st.markdown('<div class="panel-label">Live records</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    source_options = ["Proxy records", "Backend records"]
    default_index = source_options.index(default_source) if default_source in source_options else 0

    source = st.selectbox(
        "Source",
        source_options,
        index=default_index,
        key=f"source_{key_suffix}",
    )

    url = proxy_records_url if source == "Proxy records" else backend_records_url

    col1, col2 = st.columns([1, 1], gap="medium")
    with col1:
        refresh = st.button("Refresh live data", use_container_width=True, key=f"refresh_{key_suffix}")
    with col2:
        show_raw = st.checkbox("Show raw response", value=False, key=f"raw_{key_suffix}")

    if refresh:
        clear_live_cache()
        st.rerun()

    endpoint_status = proxy_status if url == proxy_records_url else backend_status
    status_label, status_color, status_detail = classify_status(endpoint_status)

    st.markdown(
        f"""
        <div class="readout-row">
            <span>Endpoint status</span>
            <strong style="color:{status_color};">{status_label}</strong>
        </div>
        <div class="readout-row">
            <span>Detail</span>
            <strong class="mono">{status_detail}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if endpoint_status["reachable"] and endpoint_status["json"] is not None and endpoint_status["ok"] and not endpoint_status["looks_like_tunnel_page"]:
        try:
            records = fetch_endpoint_records(url)
            df = safe_json_to_df(records)

            if df.empty:
                st.info("The API returned a valid live response, but it is empty.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)

            if show_raw:
                with st.expander("Raw API response", expanded=True):
                    st.json(records)
        except requests.RequestException as e:
            st.error("Failed to render live records.")
            st.code(str(e), language=None)
    else:
        if endpoint_status["looks_like_tunnel_page"]:
            st.warning("The tunnel is reachable, but it returned an interstitial/reminder page instead of JSON.")
        elif endpoint_status["reachable"] and endpoint_status["json"] is None:
            st.warning("The endpoint is reachable, but it did not return JSON.")
        elif not endpoint_status["reachable"]:
            st.error("The endpoint is unreachable.")
        else:
            st.error(f"Request failed with HTTP {endpoint_status['status_code']}.")

        with st.expander("Response preview"):
            preview = endpoint_status["text_preview"] or endpoint_status["error"] or "No response body."
            st.code(preview, language=None)

    st.markdown("</div>", unsafe_allow_html=True)


def protected_intake():
    st.markdown('<div class="panel-label">01 · Create protected record</div>', unsafe_allow_html=True)
    system_ledger(proxy_status, backend_status)

    left, right = st.columns([1.25, 0.75], gap="large")

    ttl_options = {
        "15 Seconds — Live demo": 15,
        "30 Seconds — Standard demo": 30,
        "1 Hour — Temporary cache": 3600,
        "24 Hours — Daily rotation": 86400,
        "30 Days — Compliance retention": 2592000,
        "1 Year — Enterprise archival": 31536000,
    }

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)

        with st.form("protect_form", clear_on_submit=False):
            user_name = st.text_input(
                "Customer name",
                value="",
                placeholder="Enter real customer name",
            )
            sensitive_data = st.text_input(
                "Sensitive data",
                value="",
                placeholder="Enter actual secret to protect",
                help="Example: card number, ID, SSN, account reference.",
            )
            selected_ttl = st.selectbox("Retention policy", list(ttl_options.keys()))
            submitted = st.form_submit_button("Protect Record", use_container_width=True)

        if submitted:
            if not user_name.strip() or not sensitive_data.strip():
                st.error("Customer name and sensitive data are required.")
            else:
                payload = {
                    "user_name": user_name.strip(),
                    "sensitive_data": sensitive_data.strip(),
                    "ttl_seconds": ttl_options[selected_ttl],
                }

                result = fetch_response(
                    f"{PROXY_URL}/api/records",
                    method="POST",
                    json_body=payload,
                    timeout=15,
                )

                if not result["reachable"]:
                    st.error("Could not reach the proxy. The vault may be offline or the tunnel expired.")
                    st.code(result["error"], language=None)
                elif result["looks_like_tunnel_page"]:
                    st.error("The proxy tunnel returned an interstitial page instead of the API response.")
                    st.code(result["text_preview"], language=None)
                elif result["status_code"] in (200, 201):
                    body = result["json"] if result["json"] is not None else {}
                    st.session_state.last_record_id = body.get("id")
                    st.session_state.expiry_time = time.time() + ttl_options[selected_ttl]
                    st.session_state.ttl_total = ttl_options[selected_ttl]
                    st.session_state.protected_value = sensitive_data.strip()
                    clear_live_cache()
                    st.success("Record protected. Live data updated.")
                else:
                    st.error(f"Proxy rejected the record (status {result['status_code']}).")
                    with st.expander("Response detail"):
                        if result["json"] is not None:
                            st.json(result["json"])
                        else:
                            st.code(result["text_preview"], language=None)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-label">Policy summary</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="readout-row"><span>Selected TTL</span><strong>{selected_ttl.split(" — ")[0]}</strong></div>
            <div class="readout-row"><span>Write path</span><strong>Proxy API</strong></div>
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
                f'<div style="color:{THEME["muted"]};font-size:0.82rem;">'
                f'No protected record created in this session yet.</div>',
                unsafe_allow_html=True,
            )

        if st.button("Refresh status", use_container_width=True, key="refresh_status"):
            clear_live_cache()
            st.rerun()

        st.markdown(
            f'<div style="margin-top:16px;padding-top:14px;border-top:1px solid {THEME["border"]};'
            f'color:{THEME["muted"]};font-size:0.8rem;line-height:1.5;">'
            f'The panels below reflect the latest response returned by the configured APIs.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    render_expiry_panel()
    live_records_panel(default_source="Proxy records", key_suffix="protected")


def exposure_test():
    st.markdown('<div class="panel-label">03 · Exposure test</div>', unsafe_allow_html=True)

    backend_label, backend_color, backend_detail = classify_status(backend_status)

    ledger([
        ("Inspection Source", "Backend API"),
        ("Backend Status", f"{glyph(backend_color)}{backend_label}"),
        ("Detail", backend_detail),
    ])

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-label">Direct backend inspection</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="color:{THEME["muted"]};font-size:0.84rem;line-height:1.6;">'
        f'This view queries the backend directly and shows exactly what that endpoint returns. '
        f'If the tunnel serves an interstitial or reminder page, it is flagged separately instead of being mislabeled as offline.</div>',
        unsafe_allow_html=True,
    )

    if st.button("Refresh backend check", use_container_width=True, key="refresh_backend"):
        clear_live_cache()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    live_records_panel(default_source="Backend records", key_suffix="exposure")


rail(proxy_status, backend_status)
titleblock()
page = nav_tabs()

if page == "Protected Intake":
    protected_intake()
else:
    exposure_test()
