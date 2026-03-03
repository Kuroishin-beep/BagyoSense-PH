import streamlit as st


def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@300;400;500&display=swap');

:root {
    --bg:     #08111f;
    --card:   #0d1e33;
    --border: #1a3350;
    --teal:   #00d4aa;
    --blue:   #3b82f6;
    --amber:  #f59e0b;
    --red:    #ef4444;
    --slate:  #94a3b8;
    --text:   #e2e8f0;
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp {
    background: linear-gradient(160deg, #08111f 0%, #0c1a2e 60%, #08111f 100%) !important;
}
h1,h2,h3 { font-family:'Syne',sans-serif !important; font-weight:800 !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #060e1a !important;
    border-right: 1px solid var(--border) !important;
    min-width: 220px !important;
    max-width: 220px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 1.5rem 1rem !important; }

.sb-brand {
    font-family:'Syne',sans-serif;
    font-size:1.3rem;
    font-weight:800;
    color:var(--teal);
    letter-spacing:-0.02em;
}
.sb-tagline {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.6rem;
    color:#2e4a65;
    text-transform:uppercase;
    letter-spacing:0.12em;
    margin-bottom:1rem;
}

/* Radio nav pills */
[data-testid="stRadio"] > div { gap: 2px !important; }
[data-testid="stRadio"] label {
    font-family:'Syne',sans-serif !important;
    font-size:0.82rem !important;
    font-weight:600 !important;
    color: var(--slate) !important;
    background: transparent !important;
    border-radius: 6px !important;
    padding: 0.45rem 0.8rem !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    width: 100% !important;
    display: block !important;
}
[data-testid="stRadio"] label:hover { color: var(--teal) !important; background: rgba(0,212,170,0.06) !important; }
[data-testid="stRadio"] label[data-baseweb] { padding:0 !important; }
div[role="radiogroup"] > label[data-checked="true"],
div[role="radiogroup"] > label[aria-checked="true"] {
    color: var(--teal) !important;
    background: rgba(0,212,170,0.1) !important;
}

/* Slider + multiselect */
.stSlider label, .stMultiSelect label {
    font-family:'IBM Plex Mono',monospace !important;
    font-size:0.7rem !important;
    color:var(--slate) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stMultiSelect"] > div {
    background: var(--card) !important;
    border-color: var(--border) !important;
}

/* ── Page typography ── */
.page-title {
    font-family:'Syne',sans-serif;
    font-size:2.2rem;
    font-weight:800;
    background:linear-gradient(135deg,#00d4aa 0%,#3b82f6 55%,#a855f7 100%);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    background-clip:text;
    line-height:1.15;
    margin-bottom:0.2rem;
}
.page-sub {
    font-family:'IBM Plex Mono',monospace;
    color:var(--slate);
    font-size:0.72rem;
    letter-spacing:0.16em;
    text-transform:uppercase;
    margin-bottom:1.6rem;
}
.section-tag {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.62rem;
    color:var(--teal);
    text-transform:uppercase;
    letter-spacing:0.18em;
    border:1px solid rgba(0,212,170,0.35);
    border-radius:4px;
    padding:2px 10px;
    display:inline-block;
    margin-bottom:0.55rem;
}

/* ── KPI cards ── */
.kpi-row {
    display:grid;
    grid-template-columns:repeat(5,1fr);
    gap:0.75rem;
    margin-bottom:1.4rem;
}
.kpi-card {
    background:var(--card);
    border:1px solid var(--border);
    border-radius:10px;
    padding:1rem 1.1rem;
    border-top:3px solid var(--teal);
    transition:transform 0.15s;
    overflow:hidden;
}
.kpi-card:hover { transform:translateY(-2px); }
.kpi-card.warn  { border-top-color:var(--amber); }
.kpi-card.alert { border-top-color:var(--red); }
.kpi-val {
    font-family:'Syne',sans-serif;
    font-size:1.9rem;
    font-weight:800;
    color:var(--teal);
    line-height:1;
}
.kpi-val.warn  { color:var(--amber); }
.kpi-val.alert { color:var(--red); }
.kpi-lbl {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.6rem;
    color:var(--slate);
    text-transform:uppercase;
    letter-spacing:0.08em;
    margin-top:0.3rem;
}

/* ── Insight / prediction box ── */
.insight-box {
    background:linear-gradient(135deg,#0d1e33,#112540);
    border:1px solid var(--border);
    border-radius:12px;
    padding:1.3rem 1.5rem;
    margin:0.8rem 0;
    border-left:4px solid var(--teal);
}
.insight-box.warn  { border-left-color:var(--amber); }
.insight-box.alert { border-left-color:var(--red); }

.pred-chip {
    display:inline-block;
    background:rgba(0,212,170,0.08);
    border:1px solid rgba(0,212,170,0.3);
    border-radius:20px;
    padding:3px 12px;
    font-family:'IBM Plex Mono',monospace;
    font-size:0.76rem;
    color:var(--teal);
    margin:3px;
}

/* ── AI bubble ── */
.ai-bubble {
    background:#0a1624;
    border:1px solid var(--border);
    border-radius:12px;
    padding:1.4rem 1.6rem;
    margin-top:1rem;
    line-height:1.75;
    font-size:0.93rem;
    white-space:pre-wrap;
}
.ai-header {
    font-family:'IBM Plex Mono',monospace;
    font-size:0.6rem;
    color:var(--teal);
    text-transform:uppercase;
    letter-spacing:0.18em;
    margin-bottom:0.8rem;
}

/* ── Buttons ── */
.stButton > button {
    font-family:'Syne',sans-serif !important;
    font-weight:700 !important;
    background:linear-gradient(135deg,#00d4aa,#3b82f6) !important;
    color:#050e1a !important;
    border:none !important;
    border-radius:8px !important;
    padding:0.42rem 1.3rem !important;
    font-size:0.85rem !important;
    letter-spacing:0.04em !important;
    transition:opacity 0.15s !important;
}
.stButton > button:hover { opacity:0.82 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap:0.3rem;
    background:transparent;
    border-bottom:1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    font-family:'Syne',sans-serif !important;
    font-weight:600 !important;
    color:var(--slate) !important;
    background:transparent !important;
    border:none !important;
    padding:0.4rem 0.85rem !important;
    font-size:0.82rem !important;
}
.stTabs [aria-selected="true"] {
    color:var(--teal) !important;
    border-bottom:2px solid var(--teal) !important;
}

hr { border-color:var(--border) !important; }
</style>
""", unsafe_allow_html=True)