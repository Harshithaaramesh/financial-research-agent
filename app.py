"""
app.py — Financial Research Assistant UI
Run: streamlit run app.py
Setup: python scripts/setup_auth.py  (first time only)
"""

import yaml
import streamlit as st
from pathlib import Path
from yaml.loader import SafeLoader

st.set_page_config(page_title="Financial Research Assistant", page_icon="📊", layout="wide")

# ── Auth config ────────────────────────────────────────────────────────────────
AUTH_CONFIG_PATH = Path("config/auth.yaml")
if not AUTH_CONFIG_PATH.exists():
    st.error("⚙️ Run `python scripts/setup_auth.py` first, then restart.")
    st.stop()

with open(AUTH_CONFIG_PATH) as f:
    auth_config = yaml.load(f, Loader=SafeLoader)

import streamlit_authenticator as stauth
authenticator = stauth.Authenticate(
    auth_config["credentials"],
    auth_config["cookie"]["name"],
    auth_config["cookie"]["key"],
    auth_config["cookie"]["expiry_days"],
    auto_hash=True,
)

from src.utils.report_store import init_db
init_db()

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# Note: keep HTML in st.markdown flat (≤3 spaces indent) — Streamlit treats
# 4-space indented lines as code blocks due to CommonMark parsing.
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

/* ── Page ── */
.stApp { background: #f0f4f8; }
.block-container { padding: 0 !important; max-width: 100% !important; }
header[data-testid="stHeader"] { display: none; }

/* ── Main content area: breathing room on all sides ── */
.stTabs [data-baseweb="tab-panel"] > div[data-testid="stVerticalBlock"] {
padding: 1.4rem 2rem 2rem 2rem !important;
}
/* Topbar + tab-list sit at zero padding, content area gets the padding */
.stTabs { padding: 0 !important; }

/* ── Top nav bar ── */
.topbar {
background: linear-gradient(90deg, #0d1b40 0%, #1a2f6b 100%);
padding: 0 2.4rem;
height: 58px;
display: flex;
align-items: center;
justify-content: space-between;
position: sticky;
top: 0;
z-index: 100;
box-shadow: 0 1px 0 rgba(255,255,255,0.06), 0 4px 20px rgba(0,0,0,0.25);
}
.topbar-brand {
color: #fff;
font-size: 0.95rem;
font-weight: 700;
letter-spacing: -0.2px;
display: flex;
align-items: center;
gap: 9px;
}
.topbar-brand-icon {
font-size: 1.2rem;
}
.topbar-chips { display: flex; gap: 5px; }
.topbar-chip {
background: rgba(255,255,255,0.07);
color: rgba(255,255,255,0.6);
border: 1px solid rgba(255,255,255,0.08);
border-radius: 5px;
padding: 3px 9px;
font-size: 0.65rem;
font-weight: 600;
text-transform: uppercase;
letter-spacing: 0.08em;
}
.topbar-chip.yellow {
background: rgba(250,204,21,0.12);
color: #fbbf24;
border-color: rgba(250,204,21,0.18);
}
.topbar-user { display: flex; align-items: center; gap: 10px; }
.user-avatar {
width: 30px; height: 30px;
background: linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%);
border-radius: 8px;
display: flex;
align-items: center;
justify-content: center;
font-size: 0.75rem;
font-weight: 800;
color: white;
}
.user-name { color: #f1f5f9; font-size: 0.8rem; font-weight: 600; }
.user-role { color: rgba(255,255,255,0.38); font-size: 0.68rem; font-weight: 500; }

/* ── Stat cards ── */
.stat-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 1.4rem; }
.stat-chip {
background: #fff;
border-radius: 14px;
padding: 14px 18px;
display: flex;
align-items: center;
gap: 12px;
box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04);
min-width: 140px;
border-left: 3px solid transparent;
}
.stat-chip.blue  { border-left-color: #3b82f6; }
.stat-chip.green { border-left-color: #22c55e; }
.stat-chip.slate { border-left-color: #94a3b8; }
.stat-chip-icon {
width: 36px; height: 36px;
border-radius: 10px;
display: flex;
align-items: center;
justify-content: center;
font-size: 1rem;
}
.stat-chip.blue  .stat-chip-icon { background: #eff6ff; }
.stat-chip.green .stat-chip-icon { background: #f0fdf4; }
.stat-chip.slate .stat-chip-icon { background: #f8fafc; }
.stat-chip-val { font-size: 1.25rem; font-weight: 800; color: #0f172a; line-height: 1; }
.stat-chip.blue  .stat-chip-val { color: #2563eb; }
.stat-chip.green .stat-chip-val { color: #16a34a; }
.stat-chip-lbl { font-size: 0.7rem; color: #94a3b8; font-weight: 500; margin-top: 2px; }

/* ── Cards ── */
.card {
background: #fff;
border-radius: 16px;
padding: 1.4rem 1.6rem;
box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04);
margin-bottom: 1.1rem;
border: 1px solid rgba(0,0,0,0.04);
}
.card-title {
font-size: 0.7rem;
font-weight: 700;
color: #b0bcc8;
text-transform: uppercase;
letter-spacing: 0.1em;
margin: 0 0 1rem;
}

/* ── Inputs ── */
.stTextInput > div > div > input {
background: #f8fafc !important;
border: 1.5px solid #e8edf2 !important;
border-radius: 10px !important;
color: #0f172a !important;
font-size: 0.88rem !important;
font-weight: 500 !important;
padding: 0.6rem 0.95rem !important;
transition: border-color 0.15s, box-shadow 0.15s !important;
box-shadow: none !important;
}
.stTextInput > div > div > input:focus {
border-color: #3b82f6 !important;
box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
background: #fff !important;
}
.stTextInput label {
color: #6b7a90 !important;
font-size: 0.69rem !important;
font-weight: 700 !important;
text-transform: uppercase !important;
letter-spacing: 0.09em !important;
margin-bottom: 5px !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
color: #fff !important;
border: none !important;
border-radius: 11px !important;
padding: 0.7rem 2rem !important;
font-size: 0.88rem !important;
font-weight: 700 !important;
letter-spacing: 0.01em !important;
box-shadow: 0 2px 6px rgba(37,99,235,0.25), 0 8px 20px rgba(37,99,235,0.15) !important;
transition: all 0.15s !important;
width: 100% !important;
}
.stButton > button[kind="primary"]:hover {
background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
box-shadow: 0 4px 10px rgba(37,99,235,0.3), 0 12px 28px rgba(37,99,235,0.2) !important;
transform: translateY(-1px) !important;
}
.stButton > button:not([kind="primary"]) {
border-radius: 9px !important;
font-size: 0.8rem !important;
font-weight: 600 !important;
border-color: #e2e8f0 !important;
}

/* ── Security badge pills ── */
.pill-row { display: flex; flex-wrap: wrap; gap: 7px; }
.pill {
display: inline-flex;
align-items: center;
gap: 5px;
border-radius: 7px;
padding: 5px 11px;
font-size: 0.73rem;
font-weight: 600;
}
.pill.green {
background: #f0fdf4;
color: #15803d;
}

/* ── How it works ── */
.step {
display: flex;
align-items: flex-start;
gap: 11px;
margin-bottom: 12px;
}
.step-n {
min-width: 24px; height: 24px;
background: linear-gradient(135deg, #3b82f6, #6366f1);
color: #fff;
border-radius: 7px;
display: flex;
align-items: center;
justify-content: center;
font-size: 0.65rem;
font-weight: 800;
margin-top: 0px;
flex-shrink: 0;
box-shadow: 0 2px 6px rgba(99,102,241,0.25);
}
.step-body { font-size: 0.81rem; color: #64748b; line-height: 1.5; padding-top: 3px; }
.step-body b { color: #1e293b; font-weight: 700; }

/* ── Compare headers ── */
.cmp-head {
border-radius: 12px;
padding: 11px 18px;
text-align: center;
font-weight: 700;
font-size: 0.9rem;
margin-bottom: 1rem;
}
.cmp-head.a {
background: linear-gradient(135deg, #eff6ff, #dbeafe);
color: #1d4ed8;
}
.cmp-head.b {
background: linear-gradient(135deg, #faf5ff, #ede9fe);
color: #7c3aed;
}

/* ── Report viewer ── */
.report-view {
background: #fff;
border-radius: 16px;
padding: 2rem 2.4rem;
box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04);
border: 1px solid rgba(0,0,0,0.04);
margin-top: 1rem;
}
.report-view h1 { color: #0f172a !important; font-size: 1.4rem !important; font-weight: 800 !important; letter-spacing: -0.3px !important; }
.report-view h2 {
color: #1e3a8a !important;
font-size: 0.95rem !important;
font-weight: 700 !important;
border-bottom: 1.5px solid #e0ebff;
padding-bottom: 6px;
margin-top: 1.6rem !important;
text-transform: uppercase;
letter-spacing: 0.04em;
}
.report-view p, .report-view li { color: #374151 !important; line-height: 1.8 !important; font-size: 0.88rem !important; }
.report-view strong { color: #111827 !important; }

/* ── History rows ── */
.h-row {
background: #fff;
border-radius: 13px;
padding: 13px 16px;
margin-bottom: 8px;
display: flex;
align-items: center;
gap: 14px;
box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 2px 8px rgba(0,0,0,0.03);
border: 1px solid rgba(0,0,0,0.04);
}
.h-ticker {
background: linear-gradient(135deg, #eff6ff, #dbeafe);
color: #1d4ed8;
border-radius: 8px;
padding: 6px 12px;
font-weight: 800;
font-size: 0.82rem;
min-width: 54px;
text-align: center;
letter-spacing: 0.04em;
}
.h-name { font-weight: 600; color: #1e293b; font-size: 0.86rem; }
.h-date { color: #94a3b8; font-size: 0.72rem; margin-top: 2px; }
.h-user { color: #6366f1; font-size: 0.72rem; font-weight: 600; }

/* ── Admin stat cards ── */
.a-stat {
background: #fff;
border-radius: 14px;
padding: 1.3rem 1.5rem;
text-align: center;
box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04);
border: 1px solid rgba(0,0,0,0.04);
}
.a-stat-val { font-size: 2.2rem; font-weight: 800; color: #0f172a; line-height: 1; }
.a-stat-lbl { font-size: 0.68rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.09em; margin-top: 5px; }

/* ── Section labels (replace broken card wrappers around native widgets) ── */
.section-label {
font-size: 0.69rem;
font-weight: 700;
color: #b0bcc8;
text-transform: uppercase;
letter-spacing: 0.1em;
margin: 0 0 0.85rem;
padding-bottom: 10px;
border-bottom: 1.5px solid #e8edf2;
}

/* ── Report viewer: just style the markdown content area ── */
.report-view { background: #fff; border-radius: 16px; padding: 1.6rem 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.05); border: 1px solid rgba(0,0,0,0.04); margin-bottom: 1rem; }
.report-view h1, .report-view h2, .report-view h3,
.report-view p, .report-view li, .report-view strong { all: revert; }
.report-view h1 { font-size: 1.3rem !important; font-weight: 800 !important; color: #0f172a !important; letter-spacing: -0.3px !important; margin-bottom: 1rem !important; }
.report-view h2 { font-size: 0.82rem !important; font-weight: 700 !important; color: #1e40af !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; border-bottom: 1.5px solid #dbeafe !important; padding-bottom: 5px !important; margin-top: 1.4rem !important; }
.report-view p, .report-view li { font-size: 0.88rem !important; color: #374151 !important; line-height: 1.8 !important; }
.report-view strong { font-weight: 700 !important; color: #111827 !important; }

/* ── Misc ── */
.stDownloadButton > button { border-radius: 9px !important; font-size: 0.8rem !important; font-weight: 600 !important; }
hr { border: none !important; border-top: 1px solid #f1f5f9 !important; margin: 0.8rem 0 !important; }

/* ── Pipeline progress bar ── */
[data-testid="stProgress"] > div > div {
background: linear-gradient(90deg, #3b82f6, #6366f1) !important;
border-radius: 99px !important;
transition: width 0.4s ease !important;
}
[data-testid="stProgress"] > div {
background: #f1f5f9 !important;
border-radius: 99px !important;
height: 6px !important;
}

/* ── Caption / hint text — no yellow highlight, muted colour ── */
.stCaptionContainer, [data-testid="stCaptionContainer"] {
background: transparent !important;
color: #64748b !important;
font-size: 0.76rem !important;
}
.stCaptionContainer p { color: #64748b !important; background: transparent !important; }

/* ── Tab bar ── */
.stTabs [data-baseweb="tab-list"] {
background: transparent !important;
gap: 4px !important;
border-bottom: 1.5px solid #e8edf2 !important;
padding-bottom: 0 !important;
}
.stTabs [data-baseweb="tab"] {
background: transparent !important;
border: none !important;
color: #94a3b8 !important;
font-size: 0.84rem !important;
font-weight: 600 !important;
padding: 8px 16px !important;
border-radius: 8px 8px 0 0 !important;
}
.stTabs [aria-selected="true"] {
color: #2563eb !important;
border-bottom: 2px solid #2563eb !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 0 !important; }

/* ── Streamlit status widget ── */
[data-testid="stStatusWidget"] { border-radius: 12px !important; }

/* ── Pipeline status / expander text — make it readable ── */
[data-testid="stExpander"] { background: #fff !important; border: 1px solid #e2e8f0 !important; border-radius: 14px !important; }
[data-testid="stExpanderDetails"] p,
[data-testid="stExpanderDetails"] span,
[data-testid="stExpanderDetails"] div {
color: #1e293b !important;
font-size: 0.84rem !important;
font-weight: 500 !important;
}
/* Status box (the running / complete container) */
div[data-testid="stStatusWidget"],
div[class*="StatusWidget"],
div[data-testid="element-container"] > div[style*="background"] {
background: #fff !important;
border: 1px solid #e2e8f0 !important;
border-radius: 14px !important;
}
/* Force all text inside st.status() to be dark and readable */
.stStatus { background: #f8fafc !important; border: 1.5px solid #e2e8f0 !important; border-radius: 14px !important; padding: 1rem 1.2rem !important; }
.stStatus p, .stStatus div, .stStatus span, .stStatus label {
color: #1e293b !important;
font-size: 0.84rem !important;
}
/* The st.write() lines emitted via status_cb */
[data-testid="stMarkdownContainer"] p {
color: #1e293b !important;
font-size: 0.84rem !important;
line-height: 1.6 !important;
margin: 0.2rem 0 !important;
}
/* Status header (Running pipeline for... / Complete) */
[data-testid="stStatusLabel"] {
color: #0f172a !important;
font-weight: 700 !important;
font-size: 0.88rem !important;
}

/* ── Input section label ── */
.input-section-title {
font-size: 0.68rem;
font-weight: 700;
color: #94a3b8;
text-transform: uppercase;
letter-spacing: 0.11em;
margin: 0 0 0.9rem;
padding-bottom: 0.65rem;
border-bottom: 1.5px solid #f1f5f9;
display: block;
}

/* ── Gaps around native Streamlit widget groups ── */
div[data-testid="column"] > div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
.stTextInput { margin-bottom: 0.2rem !important; }
.stButton { margin-top: 0.5rem !important; }

/* ── Streamlit native border=True containers — styled as clean cards ── */
[data-testid="stVerticalBlockBorderWrapper"] {
background: #fff !important;
border: 1px solid rgba(226,232,240,0.9) !important;
border-radius: 16px !important;
box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04) !important;
padding: 0.2rem 0.2rem !important;
margin-bottom: 0.9rem !important;
}
/* Inner padding for the container content */
[data-testid="stVerticalBlockBorderWrapper"] > div {
padding: 1.2rem 1.4rem !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
background: linear-gradient(180deg, #0d1b40 0%, #0f2050 100%) !important;
border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] * { color: #64748b !important; }
[data-testid="stSidebar"] strong, [data-testid="stSidebar"] b { color: #e2e8f0 !important; }
[data-testid="stSidebar"] p { color: #94a3b8 !important; font-size: 0.82rem !important; }
[data-testid="stSidebar"] hr { border-top-color: rgba(255,255,255,0.08) !important; }
[data-testid="stSidebar"] button {
background: rgba(255,255,255,0.06) !important;
border: 1px solid rgba(255,255,255,0.1) !important;
color: #e2e8f0 !important;
border-radius: 8px !important;
font-size: 0.82rem !important;
}
[data-testid="stSidebar"] button:hover {
background: rgba(255,255,255,0.1) !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE — only rendered when not authenticated
# ══════════════════════════════════════════════════════════════════════════════
auth_status = st.session_state.get("authentication_status")

if auth_status is not True:
    # Centre everything in a narrow column
    _, col_m, _ = st.columns([1, 1.1, 1])
    with col_m:
        st.markdown("""
<div style="text-align:center;padding:3rem 0 1.5rem">
<div style="font-size:3rem;margin-bottom:0.6rem">📊</div>
<h2 style="color:#0f172a;font-weight:800;font-size:1.6rem;margin:0 0 0.4rem;letter-spacing:-0.5px">Financial Research Assistant</h2>
<p style="color:#64748b;font-size:0.86rem;margin:0 0 2rem">Multi-agent AI &nbsp;·&nbsp; SEC EDGAR &nbsp;·&nbsp; RAG &nbsp;·&nbsp; LangGraph</p>
</div>
""", unsafe_allow_html=True)

    # Login form — always inside the not-authenticated block
    authenticator.login(location="main", fields={
        "Form name": "Sign in to continue",
        "Username": "Username",
        "Password": "Password",
        "Login": "Sign In →",
    })

    # Re-read auth status after the form submission
    auth_status = st.session_state.get("authentication_status")

    if auth_status is False:
        st.error("❌ Incorrect username or password.")

    if auth_status is not True:
        _, col_m2, _ = st.columns([1, 1.1, 1])
        with col_m2:
            st.markdown(
                '<p style="text-align:center;color:#94a3b8;font-size:0.74rem;margin-top:0.5rem">'
                'Demo &nbsp;·&nbsp; admin / Admin@123 &nbsp;·&nbsp; shreyas / Analyst@123 &nbsp;·&nbsp; demo / Demo@123'
                '</p>',
                unsafe_allow_html=True,
            )
        st.stop()   # halt — everything below only runs when authenticated

# ══════════════════════════════════════════════════════════════════════════════
# APP (authenticated)
# ══════════════════════════════════════════════════════════════════════════════
username  = st.session_state["username"]
user_name = st.session_state["name"]
role      = auth_config["credentials"]["usernames"][username].get("role", "analyst")
is_admin  = role == "admin"

from src.utils.report_store import (
    save_report, get_reports_by_user, get_all_reports,
    delete_report, log_action, get_audit_log, get_stats,
)
from src.utils.security import (
    validate_ticker, validate_company_name, validate_email,
    check_rate_limit, remaining_requests,
    ValidationError, RateLimitError,
)

if not st.session_state.get("_login_logged"):
    log_action(username, "login")
    st.session_state["_login_logged"] = True

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**{user_name}**")
    st.markdown(f"@{username} · `{role}`")
    st.markdown("---")
    authenticator.logout("Sign Out", location="sidebar")
    st.markdown("---")
    st.markdown("**Tickers**")
    st.markdown("JPM · AAPL · MSFT\nGS · GOOGL · AMZN\nNVDA · META · TSLA")

# ── Top nav bar ───────────────────────────────────────────────────────────────
remaining = remaining_requests()
admin_chip = '<span class="topbar-chip yellow">⭐ Admin</span>' if is_admin else ""
st.markdown(
    f'<div class="topbar">'
    f'<div class="topbar-brand">📊 Financial Research Assistant</div>'
    f'<div class="topbar-chips">'
    f'<span class="topbar-chip">RAG</span>'
    f'<span class="topbar-chip">LangGraph</span>'
    f'<span class="topbar-chip">Multi-Agent AI</span>'
    f'<span class="topbar-chip">SEC EDGAR</span>'
    f'{admin_chip}'
    f'</div>'
    f'<div class="topbar-user">'
    f'<div class="user-avatar">{user_name[0].upper()}</div>'
    f'<div><div class="user-name">{user_name}</div>'
    f'<div class="user-role">⚡ {remaining}/5 remaining</div></div>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_labels = ["🔎 Research", "🔄 Compare", "📁 My Reports"]
if is_admin:
    tab_labels.append("🛡 Admin Panel")

tab_objects = st.tabs(tab_labels)
tab_research = tab_objects[0]
tab_compare  = tab_objects[1]
tab_history  = tab_objects[2]
tab_admin    = tab_objects[3] if is_admin else None

# helper: render a report block
def _show_report(report_md: str, ticker: str, company: str, key_prefix: str):
    from src.utils.pdf_generator import generate_pdf
    st.markdown(report_md)
    pdf = generate_pdf(report_md, company=company, ticker=ticker)
    d1, d2 = st.columns(2)
    with d1:
        st.download_button("⬇️ Download PDF", pdf, f"{ticker}_memo.pdf", "application/pdf",
                           use_container_width=True, key=f"{key_prefix}_pdf")
    with d2:
        st.download_button("⬇️ Download Markdown", report_md, f"{ticker}_memo.md", "text/markdown",
                           use_container_width=True, key=f"{key_prefix}_md")


# ── Pipeline progress display ─────────────────────────────────────────────────
# Maps keywords in pipeline log messages → (progress %, user-friendly message)
_STAGE_MAP = [
    ("Fetching 10-K",     10, "📡 Connecting to SEC EDGAR…"),
    ("10-K:",             25, "📄 Annual report (10-K) retrieved"),
    ("News:",             35, "📰 Recent news articles gathered"),
    ("Building vector",   45, "🧠 Building AI knowledge base from documents…"),
    ("chunks created",    58, "✂️  Documents chunked and indexed"),
    ("Retrieved",         68, "🔍 Extracting key insights from filings…"),
    ("Running AI agents", 78, "⚡ AI agents at work — analysing fundamentals, risk & sentiment…"),
    ("Analysis complete", 100,"✅  Analysis complete"),
]

def _make_progress_cb(bar, label, detail):
    """Returns a status_cb that updates a progress bar + label instead of printing raw logs."""
    def _cb(msg: str):
        for keyword, pct, friendly in _STAGE_MAP:
            if keyword.lower() in msg.lower():
                bar.progress(pct)
                label.markdown(
                    f'<p style="color:#1e293b;font-size:0.88rem;font-weight:600;margin:0">'
                    f'{friendly}</p>',
                    unsafe_allow_html=True,
                )
                # Show subtle technical detail in a smaller muted line
                detail.markdown(
                    f'<p style="color:#94a3b8;font-size:0.74rem;margin:2px 0 0">{msg}</p>',
                    unsafe_allow_html=True,
                )
                return
    return _cb


def _run_with_progress(ticker: str, company: str):
    """Run the pipeline and render a clean progress UI. Returns the result dict."""
    from src.pipeline import run_pipeline

    st.markdown("""
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:1.2rem 1.4rem;margin-bottom:0.8rem">
<p style="color:#64748b;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin:0 0 0.8rem">
Analysing {company} ({ticker})</p>
""".replace("{company}", company).replace("{ticker}", ticker), unsafe_allow_html=True)

    bar   = st.progress(5)
    label = st.empty()
    detail = st.empty()
    label.markdown(
        '<p style="color:#1e293b;font-size:0.88rem;font-weight:600;margin:0">🚀 Starting pipeline…</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    result = run_pipeline(ticker, company, status_cb=_make_progress_cb(bar, label, detail))

    if result.get("error"):
        bar.progress(0)
        label.markdown(
            '<p style="color:#dc2626;font-size:0.88rem;font-weight:600;margin:0">❌ Pipeline failed</p>',
            unsafe_allow_html=True,
        )
        detail.markdown(
            f'<p style="color:#ef4444;font-size:0.78rem;margin:4px 0 0">{result["error"]}</p>',
            unsafe_allow_html=True,
        )
    else:
        bar.progress(100)
        label.markdown(
            f'<p style="color:#16a34a;font-size:0.88rem;font-weight:700;margin:0">'
            f'✅ Memo ready for {company}</p>',
            unsafe_allow_html=True,
        )
        detail.empty()

    return result


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — RESEARCH
# ══════════════════════════════════════════════════════════════════════════════
with tab_research:
    left, right = st.columns([2.4, 1], gap="large")

    with right:
        # Single markdown call — card divs actually wrap content this way
        st.markdown("""
<div class="card">
<div class="card-title">How it works</div>
<div class="step"><div class="step-n">1</div><div class="step-body"><b>Fetch</b> — SEC 10-K filing + recent news</div></div>
<div class="step"><div class="step-n">2</div><div class="step-body"><b>Index</b> — Chunk → embed → FAISS vector store</div></div>
<div class="step"><div class="step-n">3</div><div class="step-body"><b>Analyze</b> — Fundamentals · Risk · Sentiment agents</div></div>
<div class="step"><div class="step-n">4</div><div class="step-body"><b>Synthesize</b> — Coordinator writes the investment memo</div></div>
<div class="step"><div class="step-n">5</div><div class="step-body"><b>Deliver</b> — Download PDF or email directly</div></div>
</div>
<div class="card">
<div class="card-title">Security</div>
<div class="pill-row">
<span class="pill green">✓ Input validated</span>
<span class="pill green">✓ Rate limited</span>
<span class="pill green">✓ Audit logged</span>
</div>
</div>
""", unsafe_allow_html=True)

    with left:
        # Stats row
        stats_db = get_stats()
        st.markdown(
            f'<div class="stat-row">'
            f'<div class="stat-chip blue">'
            f'<div class="stat-chip-icon">⚡</div>'
            f'<div><div class="stat-chip-val">{remaining}/5</div><div class="stat-chip-lbl">Analyses left</div></div>'
            f'</div>'
            f'<div class="stat-chip green">'
            f'<div class="stat-chip-icon">📄</div>'
            f'<div><div class="stat-chip-val">{stats_db["total_reports"]}</div><div class="stat-chip-lbl">Total reports</div></div>'
            f'</div>'
            f'<div class="stat-chip slate">'
            f'<div class="stat-chip-icon">📈</div>'
            f'<div><div class="stat-chip-val">{stats_db["unique_tickers"]}</div><div class="stat-chip-lbl">Tickers covered</div></div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Input card — company required, ticker optional
        with st.container(border=True):
            st.markdown('<span class="input-section-title">Research a Company</span>', unsafe_allow_html=True)
            c1, c2 = st.columns(2, gap="medium")
            with c1:
                company_raw = st.text_input(
                    "Company Name ✱",
                    placeholder="e.g. JPMorgan Chase",
                    key="r_c",
                )
            with c2:
                ticker_raw = st.text_input(
                    "Stock Ticker  (optional)",
                    placeholder="e.g. JPM — auto-detected if blank",
                    key="r_t",
                    help="Leave blank — the ticker is looked up automatically from SEC EDGAR.",
                )
            st.markdown('<p style="color:#64748b;font-size:0.76rem;margin:0.4rem 0 0">💡 Ticker is auto-detected from SEC EDGAR if left blank.</p>', unsafe_allow_html=True)

        st.button("🔍  Generate Research Memo", type="primary", use_container_width=True, key="r_go")

        if st.session_state.get("r_go"):
            from src.utils.ticker_lookup import lookup_ticker, lookup_company
            try:
                company_name = validate_company_name(company_raw)          # required
                ticker       = validate_ticker(ticker_raw, allow_empty=True)  # optional

                # Auto-detect ticker from company name if not provided
                if not ticker:
                    with st.spinner("Looking up ticker from SEC EDGAR…"):
                        found_ticker, found_name = lookup_ticker(company_name)
                    if found_ticker:
                        ticker = found_ticker
                        company_name = found_name or company_name
                        st.info(f"🔍 Auto-detected ticker: **{ticker}** — {company_name}")
                    else:
                        st.error(
                            f"⚠️ Could not find a ticker for **{company_name}** in SEC EDGAR. "
                            "Try entering the ticker manually (e.g. AAPL, JPM)."
                        )
                        st.stop()

                check_rate_limit()
            except ValidationError as e:
                st.error(f"⚠️ {e}"); st.stop()
            except RateLimitError as e:
                st.warning(f"🚦 {e}"); st.stop()

            result = _run_with_progress(ticker, company_name)
            if result.get("error"):
                st.stop()

            save_report(ticker, company_name, result["final_report"], username=username)
            log_action(username, "report_generated", ticker=ticker, company=company_name)
            Path("outputs/reports").mkdir(parents=True, exist_ok=True)
            with open(f"outputs/reports/{ticker}_report.md", "w") as f:
                f.write(result["final_report"])
            st.session_state["r_report"] = result["final_report"]
            st.session_state["r_tkr"]    = ticker
            st.session_state["r_cmp"]    = company_name

        if "r_report" in st.session_state:
            rpt = st.session_state["r_report"]
            rtk = st.session_state["r_tkr"]
            rcp = st.session_state["r_cmp"]

            st.success(f"✅ Memo ready — **{rcp} ({rtk})**")
            st.markdown('<div class="report-view">', unsafe_allow_html=True)
            _show_report(rpt, rtk, rcp, "res")
            st.markdown('</div>', unsafe_allow_html=True)

            # Email section
            st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown('<span class="input-section-title">📤 Email this report</span>', unsafe_allow_html=True)
                email_in = st.text_input("Recipient email", placeholder="analyst@example.com", key="r_em")
            if st.button("📤 Send PDF via Email", use_container_width=True, key="r_send"):
                try:
                    clean = validate_email(email_in)
                    from src.utils.email_sender import send_pdf_report
                    from src.utils.pdf_generator import generate_pdf
                    with st.spinner(f"Sending to {clean}…"):
                        send_pdf_report(clean, generate_pdf(rpt, rcp, rtk), rcp, rtk)
                    log_action(username, "email_sent", ticker=rtk, detail=clean)
                    st.success(f"✅ Sent to **{clean}**")
                except ValidationError as e: st.error(f"⚠️ {e}")
                except EnvironmentError as e: st.error(f"⚙️ {e}")
                except Exception as e:        st.error(f"❌ {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — COMPARE
# ══════════════════════════════════════════════════════════════════════════════
with tab_compare:
    st.markdown('<h3 style="color:#0f172a;font-weight:800;margin-bottom:0.2rem;font-size:1.25rem;letter-spacing:-0.3px">Side-by-Side Comparison</h3><p style="color:#64748b;font-size:0.84rem;margin-bottom:1.3rem">Run the full pipeline for two companies and compare memos side by side.</p>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<span class="input-section-title">Enter two companies to compare</span>', unsafe_allow_html=True)
        ca, cb = st.columns(2, gap="large")
        with ca:
            st.markdown('<div class="cmp-head a">Company A</div>', unsafe_allow_html=True)
            c1 = st.text_input("Company A ✱", placeholder="e.g. JPMorgan Chase", key="cc1")
            t1 = st.text_input("Ticker A  (optional)", placeholder="e.g. JPM — auto-detected", key="ct1",
                               help="Leave blank — auto-detected from SEC EDGAR.")
        with cb:
            st.markdown('<div class="cmp-head b">Company B</div>', unsafe_allow_html=True)
            c2 = st.text_input("Company B ✱", placeholder="e.g. Goldman Sachs", key="cc2")
            t2 = st.text_input("Ticker B  (optional)", placeholder="e.g. GS — auto-detected", key="ct2",
                               help="Leave blank — auto-detected from SEC EDGAR.")
        st.markdown('<p style="color:#64748b;font-size:0.76rem;margin:0.4rem 0 0">💡 Ticker is auto-detected from SEC EDGAR if left blank.</p>', unsafe_allow_html=True)

    if st.button("🔄  Run Comparison", type="primary", use_container_width=True, key="cmp_go"):
        from src.utils.ticker_lookup import lookup_ticker

        def _resolve(ticker_raw, company_raw, label):
            """Company name is required; ticker is auto-detected if blank."""
            cp = validate_company_name(company_raw)              # required
            tk = validate_ticker(ticker_raw, allow_empty=True)   # optional
            if not tk:
                found_tk, found_name = lookup_ticker(cp)
                if not found_tk:
                    raise ValidationError(
                        f"Could not find a ticker for '{cp}' ({label}). Enter the ticker directly."
                    )
                tk = found_tk
                cp = found_name or cp
            return tk, cp

        try:
            tk1, cp1 = _resolve(t1, c1, "Company A")
            tk2, cp2 = _resolve(t2, c2, "Company B")
            check_rate_limit()
        except ValidationError as e: st.error(f"⚠️ {e}"); st.stop()
        except RateLimitError  as e: st.warning(f"🚦 {e}"); st.stop()

        ra = rb = None
        col_a, col_b = st.columns(2)
        with col_a:
            ra = _run_with_progress(tk1, cp1)
        with col_b:
            rb = _run_with_progress(tk2, cp2)

        if ra and rb and not ra["error"] and not rb["error"]:
            save_report(tk1, cp1, ra["final_report"], username=username)
            save_report(tk2, cp2, rb["final_report"], username=username)
            log_action(username, "comparison_run", detail=f"{tk1} vs {tk2}")
            st.session_state.update(cmp_ra=ra, cmp_rb=rb, cmp_tk1=tk1, cmp_cp1=cp1, cmp_tk2=tk2, cmp_cp2=cp2)

    if "cmp_ra" in st.session_state:
        ra, rb = st.session_state["cmp_ra"], st.session_state["cmp_rb"]
        tk1, cp1 = st.session_state["cmp_tk1"], st.session_state["cmp_cp1"]
        tk2, cp2 = st.session_state["cmp_tk2"], st.session_state["cmp_cp2"]

        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("10-K Size (A)", f"{ra.get('filing_len',0):,} chars")
        m2.metric("10-K Size (B)", f"{rb.get('filing_len',0):,} chars")
        m3.metric("RAG Chunks (A vs B)", f"{ra.get('chunks',0):,} / {rb.get('chunks',0):,}")

        col_a2, col_b2 = st.columns(2, gap="medium")
        with col_a2:
            st.markdown(f'<div class="cmp-head a">{tk1} — {cp1}</div>', unsafe_allow_html=True)
            _show_report(ra["final_report"], tk1, cp1, "cmp_a")
        with col_b2:
            st.markdown(f'<div class="cmp-head b">{tk2} — {cp2}</div>', unsafe_allow_html=True)
            _show_report(rb["final_report"], tk2, cp2, "cmp_b")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MY REPORTS
# ══════════════════════════════════════════════════════════════════════════════
with tab_history:
    st.markdown('<h3 style="color:#0f172a;font-weight:800;margin-bottom:0.2rem;font-size:1.25rem;letter-spacing:-0.3px">My Reports</h3><p style="color:#64748b;font-size:0.84rem;margin-bottom:1.3rem">Your personal report history — persisted across sessions.</p>', unsafe_allow_html=True)

    reports = get_reports_by_user(username)
    if not reports:
        st.info("No reports yet. Run an analysis in the Research or Compare tab.")
    else:
        from src.utils.pdf_generator import generate_pdf
        for rpt in reports:
            cm, ca2 = st.columns([5, 2])
            with cm:
                st.markdown(
                    f'<div class="h-row">'
                    f'<div class="h-ticker">{rpt["ticker"]}</div>'
                    f'<div><div class="h-name">{rpt["company"]}</div>'
                    f'<div class="h-date">🕐 {rpt["created_at"]}</div></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with ca2:
                pdf = generate_pdf(rpt["report_md"], company=rpt["company"], ticker=rpt["ticker"])
                st.download_button("⬇️ PDF", pdf, f"{rpt['ticker']}_memo.pdf",
                                   "application/pdf", key=f"h_dl_{rpt['id']}", use_container_width=True)
                if st.button("🗑 Delete", key=f"h_del_{rpt['id']}", use_container_width=True):
                    delete_report(rpt["id"])
                    log_action(username, "report_deleted", ticker=rpt["ticker"])
                    st.rerun()
            with st.expander(f"View — {rpt['ticker']}  ·  {rpt['created_at']}"):
                st.markdown(rpt["report_md"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ADMIN PANEL
# ══════════════════════════════════════════════════════════════════════════════
if is_admin and tab_admin:
    with tab_admin:
        st.markdown('<h3 style="color:#0f172a;font-weight:800;margin-bottom:0.2rem;font-size:1.25rem;letter-spacing:-0.3px">Admin Panel</h3><p style="color:#64748b;font-size:0.84rem;margin-bottom:1.3rem">Full visibility across all users — only visible to the admin role.</p>', unsafe_allow_html=True)

        stats = get_stats()
        s1, s2, s3, s4 = st.columns(4)
        for col, val, lbl in [
            (s1, stats["total_reports"],  "Total Reports"),
            (s2, stats["unique_users"],   "Unique Users"),
            (s3, stats["unique_tickers"], "Tickers Covered"),
            (s4, stats["total_logins"],   "Total Logins"),
        ]:
            with col:
                st.markdown(
                    f'<div class="a-stat"><div class="a-stat-val">{val}</div>'
                    f'<div class="a-stat-lbl">{lbl}</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)
        at1, at2 = st.tabs(["📋 All Reports", "📜 Audit Log"])

        with at1:
            all_rpts = get_all_reports()
            if not all_rpts:
                st.info("No reports yet.")
            else:
                from src.utils.pdf_generator import generate_pdf
                for rpt in all_rpts:
                    cm, ca2 = st.columns([5, 2])
                    with cm:
                        st.markdown(
                            f'<div class="h-row">'
                            f'<div class="h-ticker">{rpt["ticker"]}</div>'
                            f'<div>'
                            f'<div class="h-name">{rpt["company"]}</div>'
                            f'<div class="h-date">🕐 {rpt["created_at"]}'
                            f' &nbsp;·&nbsp; <span class="h-user">👤 {rpt["username"]}</span></div>'
                            f'</div></div>',
                            unsafe_allow_html=True,
                        )
                    with ca2:
                        pdf = generate_pdf(rpt["report_md"], company=rpt["company"], ticker=rpt["ticker"])
                        st.download_button("⬇️ PDF", pdf, f"{rpt['ticker']}_memo.pdf",
                                           "application/pdf", key=f"a_dl_{rpt['id']}", use_container_width=True)
                        if st.button("🗑 Delete", key=f"a_del_{rpt['id']}", use_container_width=True):
                            delete_report(rpt["id"])
                            log_action(username, "report_deleted", ticker=rpt["ticker"],
                                       detail=f"Deleted report by {rpt['username']}")
                            st.rerun()
                    with st.expander(f"View — {rpt['ticker']} · {rpt['username']}"):
                        st.markdown(rpt["report_md"])

        with at2:
            audit = get_audit_log(200)
            if not audit:
                st.info("Audit log is empty.")
            else:
                import pandas as pd
                df = pd.DataFrame(audit)[["timestamp", "username", "action", "ticker", "company", "detail"]]
                df.columns = ["Timestamp", "User", "Action", "Ticker", "Company", "Detail"]
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button("⬇️ Export CSV", df.to_csv(index=False),
                                   "audit_log.csv", "text/csv")
