import streamlit as st

st.set_page_config(
    page_title="BagyoSense",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Must import AFTER set_page_config
from utils.data_loader import load_data
from constants.styles import inject_css

inject_css()

# ── Load data once ────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-brand">🌀 BagyoSense</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sb-tagline">Philippines · 2014–2024</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    nav = st.radio(
        "nav",
        ["📊  Dashboard", "🔬  Analysis", "🤖  ML Predictor", "💬  AI Analyst"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        '<p style="font-family:IBM Plex Mono;font-size:0.68rem;'
        'color:#94a3b8;margin-bottom:4px">FILTERS</p>',
        unsafe_allow_html=True,
    )

    year_range = st.slider("Year range", 2014, 2024, (2014, 2024))

    enso_opts = ["El Nino", "La Nina", "Neutral"]
    selected_enso = st.multiselect("ENSO Phase", enso_opts, default=enso_opts)
    if not selected_enso:
        selected_enso = enso_opts

    st.markdown("---")
    st.markdown(
        '<p style="font-family:IBM Plex Mono;font-size:0.58rem;'
        'color:#2a4060;text-transform:uppercase;letter-spacing:0.1em">'
        'Powered by Claude AI</p>',
        unsafe_allow_html=True,
    )

# ── Filter data ───────────────────────────────────────────────────────────────
mask = (
    (df["Year"] >= year_range[0])
    & (df["Year"] <= year_range[1])
    & (df["ENSO_Phase"].isin(selected_enso))
)
dff = df[mask].copy()

# ── Route ─────────────────────────────────────────────────────────────────────
if nav == "📊  Dashboard":
    from pages.dashboard import render
    render(dff)

elif nav == "🔬  Analysis":
    from pages.analysis import render
    render(dff)

elif nav == "🤖  ML Predictor":
    from pages.predictor import render
    render(df)          # full df for training

elif nav == "💬  AI Analyst":
    from sliders.ai_analyst import render
    render(df)