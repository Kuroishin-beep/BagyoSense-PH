import streamlit as st

st.set_page_config(
    page_title="BagyoSense",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.data_loader import load_data
from utils.styles import inject_css

inject_css()

# ── Data ──────────────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = load_data()
if "nav" not in st.session_state:
    st.session_state.nav = "Dashboard"

df = st.session_state.df

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div class="sb-brand">🌀 BagyoSense</div>
        <div class="sb-tagline">Philippines · 2014–2024</div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="sb-section">Navigation</div>', unsafe_allow_html=True)

    # Button-based nav — full CSS control, no Streamlit radio quirks
    nav_items = [
        ("Dashboard",    ""),
        ("Analysis",     ""),
        ("ML Predictor", ""),
        ("AI Analyst",   ""),
    ]

    for label, icon in nav_items:
        active = st.session_state.nav == label
        cls = "nav-btn nav-btn-active" if active else "nav-btn"
        if st.button(f"{icon}  {label}", key=f"nav_{label}",
                     use_container_width=True):
            st.session_state.nav = label
            st.rerun()
        # Inject per-button active class via JS trick — handled purely in CSS below

    st.markdown("---")
    st.markdown('<div class="sb-section">Filters</div>', unsafe_allow_html=True)

    year_range = st.slider("Year range", 2014, 2024, (2014, 2024),
                           label_visibility="collapsed")
    st.markdown(
        '<div style="font-family:IBM Plex Mono;font-size:0.6rem;'
        'color:#4a6a88;margin:-6px 0 8px 2px">YEAR RANGE</div>',
        unsafe_allow_html=True,
    )

    enso_opts = ["El Nino", "La Nina", "Neutral"]
    selected_enso = st.multiselect("ENSO Phase", enso_opts, default=enso_opts,
                                   label_visibility="collapsed")
    st.markdown(
        '<div style="font-family:IBM Plex Mono;font-size:0.6rem;'
        'color:#4a6a88;margin:-6px 0 0 2px">ENSO PHASE</div>',
        unsafe_allow_html=True,
    )
    if not selected_enso:
        selected_enso = enso_opts

    st.markdown("---")
    st.markdown('<div class="sb-footer">Powered by Claude AI</div>', unsafe_allow_html=True)

# ── Filter ────────────────────────────────────────────────────────────────────
mask = (
    (df["Year"] >= year_range[0])
    & (df["Year"] <= year_range[1])
    & (df["ENSO_Phase"].isin(selected_enso))
)
dff = df[mask].copy()

# ── Route ─────────────────────────────────────────────────────────────────────
nav = st.session_state.nav

if nav == "Dashboard":
    from views.dashboard import render
    render(dff)
elif nav == "Analysis":
    from views.analysis import render
    render(dff)
elif nav == "ML Predictor":
    from views.predictor import render
    render(df)
elif nav == "AI Analyst":
    from views.ai_analyst import render
    render(df)