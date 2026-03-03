import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sb-brand">🌀 BagyoSense</div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-tagline">Philippines · 2014–2024</div>', unsafe_allow_html=True)
        st.markdown("---")

        nav = st.radio(
            "Navigation",
            ["📊 Dashboard", "🔬 Analysis", "🤖 ML Predictor", "💬 AI Analyst"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("**🔽 Filters**")

        year_range = st.slider(
            "Year Range",
            min_value=2014, max_value=2024,
            value=(2014, 2024),
            step=1
        )

        selected_enso = st.multiselect(
            "ENSO Phase",
            options=["El Niño", "La Niña", "Neutral"],
            default=["El Niño", "La Niña", "Neutral"]
        )

        if not selected_enso:
            selected_enso = ["El Niño", "La Niña", "Neutral"]

        st.markdown("---")
        st.markdown(
            '<div style="font-family:IBM Plex Mono;font-size:0.58rem;color:#2a4060;'
            'text-transform:uppercase;letter-spacing:0.1em">Powered by Claude AI</div>',
            unsafe_allow_html=True
        )

    return nav, year_range, selected_enso