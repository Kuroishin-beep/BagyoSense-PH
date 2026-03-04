import streamlit as st


def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@300;400;500&display=swap');

:root {
    --bg:        #08111f;
    --card:      #0d1e33;
    --border:    #1e3a55;
    --teal:      #00d4aa;
    --blue:      #3b82f6;
    --amber:     #f59e0b;
    --red:       #ef4444;
    --slate:     #cbd5e1;
    --slate-dim: #64748b;
    --text:      #f1f5f9;
}

/* ══ GLOBAL ══════════════════════════════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp {
    background: linear-gradient(160deg, #08111f 0%, #0b1929 60%, #08111f 100%) !important;
}
h1,h2,h3 { font-family:'Syne',sans-serif !important; font-weight:800 !important; }

/* ══ HIDE STREAMLIT CHROME ═══════════════════════════════════════════════════ */
#MainMenu, footer, header          { visibility: hidden !important; }
.stDeployButton                    { display: none !important; }
[data-testid="stSidebarNavItems"]  { display: none !important; }
[data-testid="stSidebarNavLink"]   { display: none !important; }
section[data-testid="stSidebarNav"]{ display: none !important; }
nav[data-testid="stSidebarNav"]    { display: none !important; }
/* hide the top-nav page switcher Streamlit adds for pages/ */
[data-testid="collapsedControl"]   { display: none !important; }

/* ══ SIDEBAR ════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #060d18 !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    padding: 1.4rem 1rem !important;
}

.sb-brand {
    font-family: 'Syne', sans-serif;
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--teal);
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.sb-tagline {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    color: #6a8aaa;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin-top: 2px;
    margin-bottom: 1rem;
}

/* ── Nav buttons ── */
/* Reset ALL sidebar buttons first */
[data-testid="stSidebar"] .stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    color: #00d4aa !important;
    background: rgba(0,212,170,0.06) !important;
    border: 1px solid rgba(0,212,170,0.25) !important;
    border-radius: 8px !important;
    padding: 0.6rem 0.9rem !important;
    text-align: left !important;
    justify-content: flex-start !important;
    width: 100% !important;
    margin-bottom: 3px !important;
    transition: all 0.15s ease !important;
    letter-spacing: 0.02em !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    color: #ffffff !important;
    background: rgba(0,212,170,0.16) !important;
    border-color: rgba(0,212,170,0.6) !important;
    box-shadow: 0 0 10px rgba(0,212,170,0.15) !important;
    transform: translateX(3px) !important;
}
[data-testid="stSidebar"] .stButton > button:focus,
[data-testid="stSidebar"] .stButton > button:active {
    color: #ffffff !important;
    background: linear-gradient(135deg, rgba(0,212,170,0.22), rgba(59,130,246,0.18)) !important;
    border-color: #00d4aa !important;
    box-shadow: 0 0 14px rgba(0,212,170,0.25) !important;
    outline: none !important;
}

/* ── Sidebar section labels ── */
.sb-section {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    color: #4a6a88;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin: 0.6rem 0 0.3rem 0.2rem;
}

/* ── Slider ── */
.stSlider > label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    color: #a0b4c8 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"] { color: #4a6a88 !important; font-size:0.65rem !important; }
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--teal) !important;
    border-color: var(--teal) !important;
}

/* ── Multiselect ── */
.stMultiSelect > label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    color: #a0b4c8 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stMultiSelect"] > div {
    background: #0d1e33 !important;
    border-color: #1e3a55 !important;
    color: #c0cfe0 !important;
}

/* ── Powered-by footer ── */
.sb-footer {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.56rem;
    color: #2a4060;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 0.5rem;
}

/* ══ PAGE TYPOGRAPHY ════════════════════════════════════════════════════════ */
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(1.6rem, 3vw, 2.4rem);
    font-weight: 800;
    background: linear-gradient(135deg, #00d4aa 0%, #3b82f6 55%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin-bottom: 0.2rem;
}
.page-sub {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--slate-dim);
    font-size: clamp(0.6rem, 1vw, 0.72rem);
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}
.section-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    color: var(--teal);
    text-transform: uppercase;
    letter-spacing: 0.18em;
    border: 1px solid rgba(0,212,170,0.35);
    border-radius: 4px;
    padding: 2px 10px;
    display: inline-block;
    margin-bottom: 0.5rem;
}

/* ══ KPI CARDS ══════════════════════════════════════════════════════════════ */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 0.7rem;
    margin-bottom: 1.4rem;
}
.kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.1rem;
    border-top: 3px solid var(--teal);
    transition: transform 0.15s;
    overflow: hidden;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-card.warn  { border-top-color: var(--amber); }
.kpi-card.alert { border-top-color: var(--red); }

.kpi-val {
    font-family: 'Syne', sans-serif;
    font-size: clamp(1.4rem, 2.5vw, 2rem);
    font-weight: 800;
    color: var(--teal);
    line-height: 1;
}
.kpi-val.warn  { color: var(--amber); }
.kpi-val.alert { color: var(--red); }
.kpi-lbl {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    color: var(--slate-dim);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
}

/* ══ INSIGHT / PREDICTION BOX ════════════════════════════════════════════════ */
.insight-box {
    background: linear-gradient(135deg, #0d1e33, #112540);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin: 0.7rem 0;
    border-left: 4px solid var(--teal);
}
.insight-box.warn  { border-left-color: var(--amber); }
.insight-box.alert { border-left-color: var(--red); }

.pred-chip {
    display: inline-block;
    background: rgba(0,212,170,0.08);
    border: 1px solid rgba(0,212,170,0.28);
    border-radius: 20px;
    padding: 3px 12px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: var(--teal);
    margin: 3px;
}

/* ══ AI BUBBLE ══════════════════════════════════════════════════════════════ */
.ai-bubble {
    background: #0a1624;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-top: 0.9rem;
    line-height: 1.75;
    font-size: 0.93rem;
    white-space: pre-wrap;
}
.ai-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: var(--teal);
    text-transform: uppercase;
    letter-spacing: 0.18em;
    margin-bottom: 0.8rem;
}

/* ══ BUTTONS — main content area only ═══════════════════════════════════════ */
[data-testid="stMain"] .stButton > button,
section.main .stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #00d4aa, #3b82f6) !important;
    color: #050e1a !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.42rem 1.3rem !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.04em !important;
    transition: opacity 0.15s !important;
}
[data-testid="stMain"] .stButton > button:hover,
section.main .stButton > button:hover { opacity: 0.82 !important; }

/* ══ TABS ════════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.3rem;
    background: transparent;
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: #8ba0b8 !important;
    background: transparent !important;
    border: none !important;
    padding: 0.4rem 0.85rem !important;
    font-size: 0.82rem !important;
    white-space: nowrap;
}
.stTabs [aria-selected="true"] {
    color: var(--teal) !important;
    border-bottom: 2px solid var(--teal) !important;
}

/* ══ RESPONSIVE BREAKPOINTS ═════════════════════════════════════════════════ */
/* Narrow viewport — collapse KPI grid to 2 cols */
@media (max-width: 900px) {
    .kpi-row { grid-template-columns: repeat(2, 1fr) !important; }
    .page-title { font-size: 1.6rem !important; }
}
@media (max-width: 600px) {
    .kpi-row { grid-template-columns: 1fr 1fr !important; }
    .kpi-val  { font-size: 1.4rem !important; }
    .insight-box { padding: 0.9rem 1rem !important; }
}

/* ══ MISC ════════════════════════════════════════════════════════════════════ */
hr { border-color: var(--border) !important; }
[data-testid="stDataFrame"] { background: var(--card) !important; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)