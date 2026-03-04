import streamlit as st
import pandas as pd
import anthropic


def _build_context(df: pd.DataFrame) -> str:
    yearly   = df.groupby("Year")["Number_of_Typhoons"].sum().to_dict()
    monthly  = df.groupby("Month")["Number_of_Typhoons"].mean().round(2).to_dict()
    enso_avg = df.groupby("ENSO_Phase")["Number_of_Typhoons"].mean().round(2).to_dict()
    corr = (
        df[["Number_of_Typhoons","ONI","Western_Pacific_SST",
            "Vertical_Wind_Shear","Midlevel_Humidity","SeaLevelPressure"]]
        .corr()["Number_of_Typhoons"].drop("Number_of_Typhoons").round(3).to_dict()
    )
    return f"""
You are a senior meteorologist and climate data scientist at PAGASA.
You are analyzing 10 years of Philippines typhoon data (2014-2024).

DATASET: 132 monthly observations.
Features: Number_of_Typhoons, ONI, Nino3.4 SST anomaly, Western Pacific SST,
Vertical Wind Shear, Midlevel Humidity, Sea Level Pressure, MJO Phase, Prev month typhoons.

KEY STATISTICS:
- Total typhoons (2014-2024): {df['Number_of_Typhoons'].sum()}
- Annual totals: {yearly}
- Monthly averages: {monthly}
- Average by ENSO phase: {enso_avg}
- Correlations with typhoon count: {corr}

KEY PATTERNS:
- Peak season is June-November (~85% of all typhoons)
- July-October are most active months
- La Nina correlates with higher typhoon counts; El Nino suppresses activity
- Vertical wind shear is the strongest negative predictor
- Previous month count is the strongest short-term positive predictor

GUIDELINES:
- Be precise; cite specific numbers from the statistics
- Use professional meteorological language
- For longer answers, use concise bold headers
- Plain text only, no markdown code blocks
- Limit to ~400-600 words unless a full report is requested
""".strip()


PRESETS = [
    ("Annual Trends",    "What are the key trends in Philippines typhoon frequency from 2014 to 2024?"),
    (" ENSO Influence",   "How do El Nino and La Nina affect typhoon frequency? What does the data show?"),
    (" Climate Drivers",  "Which climate variables are the strongest predictors of typhoon formation?"),
    (" Peak Season",      "What factors drive peak typhoon season (June-November)?"),
    (" Future Outlook",   "What can we infer about future typhoon activity based on observed patterns?"),
    (" Worst Years",      "What climate conditions drove the most active typhoon years?"),
]


def render(df: pd.DataFrame):
    st.markdown('<div class="page-title">AI Analyst</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Claude-Powered Typhoon Intelligence</div>', unsafe_allow_html=True)

    context = _build_context(df)

    # ── Preset buttons ────────────────────────────────────────────────────────
    st.markdown('<div class="section-tag">QUICK INSIGHTS</div>', unsafe_allow_html=True)
    pcols = st.columns(3)
    for i, (label, question) in enumerate(PRESETS):
        with pcols[i % 3]:
            if st.button(label, key=f"preset_{i}"):
                st.session_state["ai_q"] = question
                st.rerun()

    st.markdown("---")

    # ── Free Q&A ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-tag">ASK THE ANALYST</div>', unsafe_allow_html=True)
    question = st.text_area(
        "question",
        value=st.session_state.get("ai_q",""),
        placeholder="e.g. How does MJO phase interact with ENSO to influence typhoon activity?",
        height=90,
        label_visibility="collapsed",
    )

    col_btn, _ = st.columns([1,5])
    with col_btn:
        analyze = st.button("Analyze", key="analyze_btn")

    if analyze and question.strip():
        with st.spinner("Claude is analyzing…"):
            try:
                client = anthropic.Anthropic()
                resp = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1200,
                    system=context,
                    messages=[{"role":"user","content":question}],
                )
                st.markdown(f"""
                <div class="ai-bubble">
                    <div class="ai-header">Claude · Meteorological Analysis</div>
                    {resp.content[0].text}
                </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"API error: {e}")
    elif analyze:
        st.warning("Please enter a question.")

    # ── Auto report ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-tag">FULL ANALYTICAL REPORT</div>', unsafe_allow_html=True)
    st.caption("Generate a structured 6-section report covering all major findings.")

    if st.button("Generate Report", key="report_btn"):
        with st.spinner("Generating report…"):
            try:
                client = anthropic.Anthropic()
                prompt = """Generate a comprehensive analytical report on Philippines typhoon data (2014-2024).
Structure:
**Executive Summary** — 3-4 sentences.
**Key Findings** — 5 bullet points with specific numbers.
**ENSO-Typhoon Relationship** — 2-3 paragraphs.
**Climate Driver Analysis** — rank and explain top 3-4 variables.
**Seasonal Risk Assessment** — monthly risk profile.
**Recommendations** — 3 actionable recommendations for early warning.
Keep total to ~650 words. Plain text only."""
                resp = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1600,
                    system=context,
                    messages=[{"role":"user","content":prompt}],
                )
                st.markdown(f"""
                <div class="ai-bubble">
                    <div class="ai-header">BagyoSense Analytical Report · Claude AI</div>
                    {resp.content[0].text}
                </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"API error: {e}")