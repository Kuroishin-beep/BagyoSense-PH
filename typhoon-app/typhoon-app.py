import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import anthropic
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings("ignore")

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌀 BagyoSense",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@300;400;500&display=swap');

:root {
    --typhoon-blue: #0a1628;
    --storm-teal: #00d4aa;
    --warning-amber: #f59e0b;
    --danger-red: #ef4444;
    --calm-slate: #94a3b8;
    --card-bg: #0f2035;
    --border: #1e3a5f;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--typhoon-blue);
    color: #e2e8f0;
}

.stApp {
    background: linear-gradient(135deg, #0a1628 0%, #0d1f3c 50%, #0a1628 100%);
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00d4aa, #3b82f6, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}

.hero-sub {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--calm-slate);
    font-size: 0.85rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

.metric-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    border-left: 3px solid var(--storm-teal);
    transition: transform 0.2s;
}

.metric-card:hover { transform: translateY(-2px); }

.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: var(--storm-teal);
    line-height: 1;
}

.metric-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: var(--calm-slate);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.3rem;
}

.section-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: var(--storm-teal);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    border: 1px solid var(--storm-teal);
    border-radius: 4px;
    padding: 2px 8px;
    display: inline-block;
    margin-bottom: 0.5rem;
}

.insight-box {
    background: linear-gradient(135deg, #0f2035, #162a45);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 0.8rem 0;
    border-left: 4px solid var(--storm-teal);
}

.insight-box.warning {
    border-left-color: var(--warning-amber);
}

.insight-box.danger {
    border-left-color: var(--danger-red);
}

.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #00d4aa, #3b82f6) !important;
    color: #0a1628 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    transition: opacity 0.2s !important;
}

.stButton > button:hover { opacity: 0.85 !important; }

.ai-response {
    background: #0f2035;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1rem;
    line-height: 1.7;
    font-size: 0.95rem;
}

.ai-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: var(--storm-teal);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 6px;
}

.stSelectbox > div > div,
.stSlider > div,
.stTextArea > div > div {
    background: var(--card-bg) !important;
    border-color: var(--border) !important;
    color: #e2e8f0 !important;
}

div[data-testid="stSidebarContent"] {
    background: #080f1e;
    border-right: 1px solid var(--border);
}

.sidebar-brand {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    color: var(--storm-teal);
    margin-bottom: 0.3rem;
}

hr {
    border-color: var(--border) !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: transparent;
    border-bottom: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: var(--calm-slate) !important;
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 1rem !important;
}

.stTabs [aria-selected="true"] {
    color: var(--storm-teal) !important;
    border-bottom: 2px solid var(--storm-teal) !important;
}

.prediction-chip {
    display: inline-block;
    background: linear-gradient(135deg, rgba(0,212,170,0.15), rgba(59,130,246,0.15));
    border: 1px solid rgba(0,212,170,0.4);
    border-radius: 20px;
    padding: 4px 14px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    color: var(--storm-teal);
    margin: 3px;
}

.stDataFrame {
    background: var(--card-bg) !important;
}
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\IT Intern\Documents\GitHub\BagyoSense-PH\typhoon-app\dataset\philippines_typhoon_monthly_2014_2024.csv")
    # Feature engineering
    month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                   7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    df["Month_Name"] = df["Month"].map(month_names)
    df["Date"] = pd.to_datetime(df[["Year","Month"]].assign(DAY=1))
    df["Season"] = df["Month"].apply(lambda m: "Peak (Jun-Nov)" if 6<=m<=11 else "Off-Season (Dec-May)")
    df["ENSO_Phase"] = df["ONI"].apply(lambda x: "El Niño" if x>=0.5 else ("La Niña" if x<=-0.5 else "Neutral"))
    df["Typhoon_Category"] = df["Number_of_Typhoons"].apply(
        lambda x: "None" if x==0 else ("Low (1-2)" if x<=2 else ("Moderate (3-4)" if x<=4 else "High (5+)"))
    )
    return df

df = load_data()

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🌀 BagyoSense</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono;font-size:0.65rem;color:#64748b;letter-spacing:0.1em;margin-bottom:1.5rem">PHILIPPINES · 2014–2024</div>', unsafe_allow_html=True)
    st.markdown("---")

    nav = st.radio(
        "Navigate",
        ["📊 Dashboard", "🔬 Analysis", "🤖 ML Predictor", "💬 AI Analyst"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**Filter Data**")
    year_range = st.slider("Year Range", 2014, 2024, (2014, 2024))
    selected_enso = st.multiselect(
        "ENSO Phase",
        ["El Niño", "La Niña", "Neutral"],
        default=["El Niño", "La Niña", "Neutral"]
    )

    st.markdown("---")
    st.markdown('<div style="font-family:IBM Plex Mono;font-size:0.65rem;color:#64748b">POWERED BY CLAUDE 3.5 SONNET</div>', unsafe_allow_html=True)

# Filter data
mask = (
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1]) &
    (df["ENSO_Phase"].isin(selected_enso))
)
dff = df[mask].copy()

# ─── PLOTLY THEME ──────────────────────────────────────────────────────────────
PLOT_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,32,53,0.6)",
    font=dict(family="IBM Plex Mono", color="#94a3b8", size=11),
    xaxis=dict(gridcolor="#1e3a5f", linecolor="#1e3a5f", tickcolor="#94a3b8"),
    yaxis=dict(gridcolor="#1e3a5f", linecolor="#1e3a5f", tickcolor="#94a3b8"),
    colorway=["#00d4aa","#3b82f6","#a855f7","#f59e0b","#ef4444","#10b981"],
)

# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD TAB
# ═══════════════════════════════════════════════════════════════════════════════
if nav == "📊 Dashboard":
    st.markdown('<div class="hero-title">BagyoSense</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Philippines Typhoon Intelligence · 10-Year Climate Analytics · 2014–2024</div>', unsafe_allow_html=True)

    # KPI Row
    total = dff["Number_of_Typhoons"].sum()
    avg_annual = dff.groupby("Year")["Number_of_Typhoons"].sum().mean()
    peak_month = dff.groupby("Month_Name")["Number_of_Typhoons"].mean().idxmax()
    worst_year = dff.groupby("Year")["Number_of_Typhoons"].sum().idxmax()
    peak_season_pct = dff[dff["Season"]=="Peak (Jun-Nov)"]["Number_of_Typhoons"].sum() / total * 100

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, val, label in zip(
        [c1, c2, c3, c4, c5],
        [total, f"{avg_annual:.1f}", peak_month, worst_year, f"{peak_season_pct:.0f}%"],
        ["Total Typhoons", "Avg / Year", "Peak Month", "Most Active Year", "Peak Season Share"]
    ):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1 Charts
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="section-tag">TIMELINE</div>', unsafe_allow_html=True)
        yearly = dff.groupby("Year")["Number_of_Typhoons"].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=yearly["Year"], y=yearly["Number_of_Typhoons"],
            marker=dict(
                color=yearly["Number_of_Typhoons"],
                colorscale=[[0,"#1e3a5f"],[0.5,"#00d4aa"],[1,"#3b82f6"]],
                showscale=False
            ),
            text=yearly["Number_of_Typhoons"],
            textposition="outside",
            textfont=dict(color="#94a3b8", size=10)
        ))
        # Trend line
        z = np.polyfit(yearly["Year"], yearly["Number_of_Typhoons"], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=yearly["Year"], y=p(yearly["Year"]),
            mode="lines", name="Trend",
            line=dict(color="#f59e0b", dash="dash", width=2)
        ))
        fig.update_layout(**PLOT_THEME, title=None, height=280,
                          margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                          bargap=0.25)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-tag">BY ENSO PHASE</div>', unsafe_allow_html=True)
        enso_counts = dff.groupby("ENSO_Phase")["Number_of_Typhoons"].sum().reset_index()
        fig2 = go.Figure(go.Pie(
            labels=enso_counts["ENSO_Phase"],
            values=enso_counts["Number_of_Typhoons"],
            hole=0.55,
            marker=dict(colors=["#ef4444","#3b82f6","#00d4aa"],
                        line=dict(color="#0a1628", width=3)),
            textfont=dict(family="IBM Plex Mono", size=10),
        ))
        fig2.update_layout(**PLOT_THEME, height=280,
                           margin=dict(l=0,r=0,t=10,b=0),
                           showlegend=True,
                           legend=dict(font=dict(size=10)))
        st.plotly_chart(fig2, use_container_width=True)

    # Row 2 Charts
    col3, col4 = st.columns([1, 2])

    with col3:
        st.markdown('<div class="section-tag">MONTHLY PATTERN</div>', unsafe_allow_html=True)
        monthly_avg = dff.groupby("Month")["Number_of_Typhoons"].mean().reset_index()
        month_map = {1:"J",2:"F",3:"M",4:"A",5:"M",6:"J",7:"J",8:"A",9:"S",10:"O",11:"N",12:"D"}
        monthly_avg["M"] = monthly_avg["Month"].map(month_map)
        fig3 = go.Figure(go.Bar(
            x=monthly_avg["M"], y=monthly_avg["Number_of_Typhoons"],
            marker=dict(
                color=monthly_avg["Number_of_Typhoons"],
                colorscale=[[0,"#1e3a5f"],[1,"#00d4aa"]],
            )
        ))
        fig3.update_layout(**PLOT_THEME, height=260, margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-tag">CLIMATE CORRELATIONS</div>', unsafe_allow_html=True)
        features = ["ONI","Western_Pacific_SST","Vertical_Wind_Shear","Midlevel_Humidity","SeaLevelPressure"]
        corr = dff[features + ["Number_of_Typhoons"]].corr()["Number_of_Typhoons"].drop("Number_of_Typhoons")
        colors = ["#ef4444" if v < 0 else "#00d4aa" for v in corr.values]
        fig4 = go.Figure(go.Bar(
            x=corr.values, y=corr.index,
            orientation='h',
            marker=dict(color=colors)
        ))
        fig4.update_layout(**PLOT_THEME, height=260, margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                           xaxis=dict(range=[-0.7, 0.7], **PLOT_THEME["xaxis"]))
        fig4.add_vline(x=0, line_color="#1e3a5f", line_width=1)
        st.plotly_chart(fig4, use_container_width=True)

    # Heatmap
    st.markdown('<div class="section-tag">YEAR × MONTH HEATMAP</div>', unsafe_allow_html=True)
    pivot = dff.pivot_table(values="Number_of_Typhoons", index="Year", columns="Month", aggfunc="sum", fill_value=0)
    pivot.columns = [month_map.get(c, c) for c in pivot.columns]
    fig5 = go.Figure(go.Heatmap(
        z=pivot.values, x=list(pivot.columns), y=list(pivot.index),
        colorscale=[[0,"#0a1628"],[0.3,"#1e3a5f"],[0.7,"#00d4aa"],[1,"#3b82f6"]],
        showscale=True,
        text=pivot.values, texttemplate="%{text}",
        textfont=dict(size=10, color="#e2e8f0")
    ))
    fig5.update_layout(**PLOT_THEME, height=300, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig5, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS TAB
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "🔬 Analysis":
    st.markdown("## Deep Analysis", unsafe_allow_html=False)
    st.markdown('<div class="hero-sub">MULTI-VARIABLE CLIMATE INVESTIGATION</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🌊 ENSO Impact", "🌡️ Climate Drivers", "📐 Statistics"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-tag">ROLLING AVERAGE</div>', unsafe_allow_html=True)
            monthly_ts = dff.sort_values("Date")[["Date","Number_of_Typhoons"]].copy()
            monthly_ts["Rolling12"] = monthly_ts["Number_of_Typhoons"].rolling(12, min_periods=1).mean()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=monthly_ts["Date"], y=monthly_ts["Number_of_Typhoons"],
                                  name="Monthly", marker_color="#1e3a5f", opacity=0.7))
            fig.add_trace(go.Scatter(x=monthly_ts["Date"], y=monthly_ts["Rolling12"],
                                      name="12-Mo Avg", line=dict(color="#00d4aa", width=2.5)))
            fig.update_layout(**PLOT_THEME, height=320, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-tag">CUMULATIVE TYPHOONS</div>', unsafe_allow_html=True)
            for yr, grp in dff.sort_values(["Year","Month"]).groupby("Year"):
                grp = grp.reset_index()
                grp["cum"] = grp["Number_of_Typhoons"].cumsum()
                alpha = 0.3 + 0.07*(yr-2014)
                color = f"rgba(0,212,170,{min(alpha,1.0)})"
                st.session_state  # just to avoid issues

            fig2 = go.Figure()
            for yr, grp in dff.sort_values(["Year","Month"]).groupby("Year"):
                grp = grp.reset_index()
                grp["cum"] = grp["Number_of_Typhoons"].cumsum()
                alpha = 0.25 + 0.07*(yr-2014)
                fig2.add_trace(go.Scatter(
                    x=grp["Month"], y=grp["cum"],
                    mode="lines+markers", name=str(yr),
                    line=dict(width=1.5),
                    marker=dict(size=4)
                ))
            fig2.update_layout(**PLOT_THEME, height=320, margin=dict(l=0,r=0,t=10,b=0),
                               xaxis=dict(tickvals=list(range(1,13)),
                                          ticktext=["J","F","M","A","M","J","J","A","S","O","N","D"]))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-tag">SEASONAL DECOMPOSITION</div>', unsafe_allow_html=True)
        season_year = dff.groupby(["Year","Season"])["Number_of_Typhoons"].sum().reset_index()
        fig3 = px.bar(season_year, x="Year", y="Number_of_Typhoons", color="Season",
                      color_discrete_map={"Peak (Jun-Nov)":"#00d4aa","Off-Season (Dec-May)":"#1e3a5f"},
                      barmode="group")
        fig3.update_layout(**PLOT_THEME, height=280, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-tag">ENSO PHASE BREAKDOWN</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            enso_box = dff.groupby(["ENSO_Phase", "Year"])["Number_of_Typhoons"].sum().reset_index()
            fig = px.box(enso_box, x="ENSO_Phase", y="Number_of_Typhoons",
                         color="ENSO_Phase",
                         color_discrete_map={"El Niño":"#ef4444","La Niña":"#3b82f6","Neutral":"#00d4aa"})
            fig.update_layout(**PLOT_THEME, height=320, margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                              title="Annual Typhoon Count by ENSO Phase")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            oni_scatter = dff.copy()
            fig2 = px.scatter(oni_scatter, x="ONI", y="Number_of_Typhoons",
                              color="ENSO_Phase", size="Number_of_Typhoons",
                              hover_data=["Year","Month_Name"],
                              color_discrete_map={"El Niño":"#ef4444","La Niña":"#3b82f6","Neutral":"#00d4aa"},
                              trendline="ols")
            fig2.update_layout(**PLOT_THEME, height=320, margin=dict(l=0,r=0,t=10,b=0),
                               title="ONI vs Typhoon Count")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-tag">ONI TIME SERIES WITH TYPHOON INTENSITY</div>', unsafe_allow_html=True)
        fig3 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                              subplot_titles=("ONI Index (ENSO Signal)", "Monthly Typhoon Count"))
        fig3.add_trace(go.Scatter(x=dff["Date"], y=dff["ONI"], fill="tozeroy",
                                   fillcolor="rgba(0,212,170,0.1)",
                                   line=dict(color="#00d4aa", width=1.5), name="ONI"), row=1, col=1)
        fig3.add_hrect(y0=0.5, y1=dff["ONI"].max()+0.1, fillcolor="rgba(239,68,68,0.07)",
                       line_width=0, row=1, col=1)
        fig3.add_hrect(y0=dff["ONI"].min()-0.1, y1=-0.5, fillcolor="rgba(59,130,246,0.07)",
                       line_width=0, row=1, col=1)
        fig3.add_trace(go.Bar(x=dff["Date"], y=dff["Number_of_Typhoons"],
                               marker_color="#3b82f6", name="Typhoons"), row=2, col=1)
        fig3.update_layout(**PLOT_THEME, height=400, margin=dict(l=0,r=0,t=30,b=0), showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-tag">MULTI-VARIABLE SCATTER MATRIX</div>', unsafe_allow_html=True)
        features_select = ["Number_of_Typhoons","ONI","Western_Pacific_SST",
                           "Vertical_Wind_Shear","Midlevel_Humidity","SeaLevelPressure"]
        fig = px.scatter_matrix(dff[features_select],
                                dimensions=features_select,
                                color=dff["ENSO_Phase"],
                                color_discrete_map={"El Niño":"#ef4444","La Niña":"#3b82f6","Neutral":"#00d4aa"},
                                opacity=0.5)
        fig.update_traces(diagonal_visible=False, marker=dict(size=3))
        fig.update_layout(**PLOT_THEME, height=550, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-tag">WIND SHEAR vs TYPHOONS</div>', unsafe_allow_html=True)
            fig2 = px.scatter(dff, x="Vertical_Wind_Shear", y="Number_of_Typhoons",
                              color="Season", size="Number_of_Typhoons",
                              hover_data=["Year","Month_Name"],
                              color_discrete_map={"Peak (Jun-Nov)":"#00d4aa","Off-Season (Dec-May)":"#3b82f6"},
                              trendline="ols")
            fig2.update_layout(**PLOT_THEME, height=300, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig2, use_container_width=True)

        with col2:
            st.markdown('<div class="section-tag">SST vs TYPHOONS</div>', unsafe_allow_html=True)
            fig3 = px.scatter(dff, x="Western_Pacific_SST", y="Number_of_Typhoons",
                              color="ENSO_Phase",
                              color_discrete_map={"El Niño":"#ef4444","La Niña":"#3b82f6","Neutral":"#00d4aa"},
                              trendline="ols")
            fig3.update_layout(**PLOT_THEME, height=300, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig3, use_container_width=True)

    with tab4:
        st.markdown('<div class="section-tag">DESCRIPTIVE STATISTICS</div>', unsafe_allow_html=True)
        desc = dff[["Number_of_Typhoons","ONI","Western_Pacific_SST",
                    "Vertical_Wind_Shear","Midlevel_Humidity","SeaLevelPressure"]].describe().round(3)
        st.dataframe(desc, use_container_width=True)

        st.markdown('<div class="section-tag">CORRELATION MATRIX</div>', unsafe_allow_html=True)
        corr_mat = dff[["Number_of_Typhoons","ONI","Western_Pacific_SST",
                        "Vertical_Wind_Shear","Midlevel_Humidity","SeaLevelPressure",
                        "Prev_month_typhoons"]].corr()
        fig_corr = go.Figure(go.Heatmap(
            z=corr_mat.values,
            x=corr_mat.columns.tolist(),
            y=corr_mat.columns.tolist(),
            colorscale=[[0,"#3b82f6"],[0.5,"#0f2035"],[1,"#ef4444"]],
            zmin=-1, zmax=1,
            text=corr_mat.round(2).values,
            texttemplate="%{text}",
            textfont=dict(size=9)
        ))
        fig_corr.update_layout(**PLOT_THEME, height=380, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_corr, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ML PREDICTOR TAB
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "🤖 ML Predictor":
    st.markdown("## ML Typhoon Predictor", unsafe_allow_html=False)
    st.markdown('<div class="hero-sub">MACHINE LEARNING · PREDICTIVE MODELING</div>', unsafe_allow_html=True)

    FEATURES = ["Month","ONI","Nino3.4_SST_anomaly","Western_Pacific_SST",
                "Vertical_Wind_Shear","Midlevel_Humidity","SeaLevelPressure",
                "MJO_Phase","Prev_month_typhoons"]
    TARGET = "Number_of_Typhoons"

    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)

    @st.cache_data
    def train_models():
        models = {
            "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42),
            "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, max_depth=4, random_state=42),
            "Linear Regression": LinearRegression()
        }
        results = {}
        for name, m in models.items():
            if name == "Linear Regression":
                m.fit(X_train_sc, y_train)
                preds = m.predict(X_test_sc)
            else:
                m.fit(X_train, y_train)
                preds = m.predict(X_test)
            preds_clipped = np.clip(np.round(preds), 0, None)
            results[name] = {
                "model": m,
                "preds": preds_clipped,
                "r2": r2_score(y_test, preds_clipped),
                "rmse": np.sqrt(mean_squared_error(y_test, preds_clipped)),
                "mae": mean_absolute_error(y_test, preds_clipped),
            }
        return results, y_test

    with st.spinner("Training models..."):
        model_results, y_test_vals = train_models()

    # Model comparison
    st.markdown('<div class="section-tag">MODEL PERFORMANCE</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    for i, (name, res) in enumerate(model_results.items()):
        col = [col1, col2, col3][i]
        with col:
            emoji = "🏆" if res["r2"] == max(r["r2"] for r in model_results.values()) else "📊"
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-family:Syne;font-weight:700;color:#e2e8f0;margin-bottom:0.5rem">{emoji} {name}</div>
                <div style="display:flex;gap:1rem;flex-wrap:wrap">
                    <div><span class="prediction-chip">R² {res['r2']:.3f}</span></div>
                    <div><span class="prediction-chip">RMSE {res['rmse']:.2f}</span></div>
                    <div><span class="prediction-chip">MAE {res['mae']:.2f}</span></div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Best model details
    best_name = max(model_results, key=lambda k: model_results[k]["r2"])
    best = model_results[best_name]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<div class="section-tag">ACTUAL vs PREDICTED — {best_name}</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(len(y_test_vals))), y=list(y_test_vals),
                                  name="Actual", line=dict(color="#00d4aa", width=2)))
        fig.add_trace(go.Scatter(x=list(range(len(best["preds"]))), y=list(best["preds"]),
                                  name="Predicted", line=dict(color="#f59e0b", dash="dash", width=2)))
        fig.update_layout(**PLOT_THEME, height=300, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-tag">FEATURE IMPORTANCE</div>', unsafe_allow_html=True)
        rf_model = model_results["Random Forest"]["model"]
        importances = rf_model.feature_importances_
        feat_df = pd.DataFrame({"Feature": FEATURES, "Importance": importances}).sort_values("Importance")
        fig2 = go.Figure(go.Bar(
            x=feat_df["Importance"], y=feat_df["Feature"],
            orientation="h",
            marker=dict(color=feat_df["Importance"],
                        colorscale=[[0,"#1e3a5f"],[1,"#00d4aa"]])
        ))
        fig2.update_layout(**PLOT_THEME, height=300, margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Interactive Predictor
    st.markdown("---")
    st.markdown('<div class="section-tag">🎯 INTERACTIVE PREDICTOR</div>', unsafe_allow_html=True)
    st.markdown("**Adjust climate parameters to predict typhoon count**")

    c1, c2, c3 = st.columns(3)
    with c1:
        pred_month = st.slider("Month", 1, 12, 8)
        pred_oni = st.slider("ONI Index", -2.5, 2.5, 0.0, 0.1)
        pred_nino = st.slider("Niño 3.4 SST Anomaly", -2.5, 2.5, 0.0, 0.1)
    with c2:
        pred_sst = st.slider("W. Pacific SST Anomaly", -1.5, 1.5, 0.0, 0.05)
        pred_shear = st.slider("Vertical Wind Shear", 5.0, 16.0, 8.0, 0.1)
        pred_humidity = st.slider("Midlevel Humidity (%)", 45.0, 80.0, 68.0, 0.5)
    with c3:
        pred_slp = st.slider("Sea Level Pressure (hPa)", 1003.0, 1012.0, 1005.0, 0.1)
        pred_mjo = st.slider("MJO Phase", 0, 8, 4)
        pred_prev = st.slider("Previous Month Typhoons", 0, 8, 1)

    input_arr = np.array([[pred_month, pred_oni, pred_nino, pred_sst,
                           pred_shear, pred_humidity, pred_slp, pred_mjo, pred_prev]])

    rf_pred = int(np.clip(round(model_results["Random Forest"]["model"].predict(input_arr)[0]), 0, 12))
    gb_pred = int(np.clip(round(model_results["Gradient Boosting"]["model"].predict(input_arr)[0]), 0, 12))
    lr_pred = int(np.clip(round(model_results["Linear Regression"]["model"].predict(scaler.transform(input_arr))[0]), 0, 12))
    ensemble = round((rf_pred + gb_pred + lr_pred) / 3, 1)

    month_names_full = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
                        7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
    enso_label = "El Niño" if pred_oni >= 0.5 else ("La Niña" if pred_oni <= -0.5 else "Neutral ENSO")

    st.markdown(f"""
    <div class="insight-box">
        <div style="font-family:Syne;font-weight:800;font-size:1.1rem;margin-bottom:0.8rem;color:#e2e8f0">
            Prediction for {month_names_full[pred_month]} · {enso_label}
        </div>
        <div style="display:flex;gap:1.5rem;flex-wrap:wrap;align-items:center">
            <div>
                <div style="font-family:IBM Plex Mono;font-size:0.65rem;color:#94a3b8;text-transform:uppercase">ENSEMBLE</div>
                <div style="font-family:Syne;font-size:2.8rem;font-weight:800;color:#00d4aa;line-height:1">{ensemble}</div>
                <div style="font-family:IBM Plex Mono;font-size:0.65rem;color:#94a3b8">TYPHOONS EXPECTED</div>
            </div>
            <div style="display:flex;gap:0.8rem">
                <span class="prediction-chip">🌲 RF: {rf_pred}</span>
                <span class="prediction-chip">📈 GB: {gb_pred}</span>
                <span class="prediction-chip">📏 LR: {lr_pred}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# AI ANALYST TAB
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "💬 AI Analyst":
    st.markdown("## Claude AI Analyst", unsafe_allow_html=False)
    st.markdown('<div class="hero-sub">LLM-POWERED TYPHOON INTELLIGENCE</div>', unsafe_allow_html=True)

    # Build data summary for context
    yearly_summary = df.groupby("Year")["Number_of_Typhoons"].sum().to_dict()
    monthly_avg = df.groupby("Month")["Number_of_Typhoons"].mean().round(2).to_dict()
    enso_avg = df.groupby("ENSO_Phase")["Number_of_Typhoons"].mean().round(2).to_dict()
    corr_with_target = df[["Number_of_Typhoons","ONI","Western_Pacific_SST",
                           "Vertical_Wind_Shear","Midlevel_Humidity","SeaLevelPressure"]].corr()["Number_of_Typhoons"].round(3).to_dict()

    DATA_CONTEXT = f"""
You are a senior meteorologist and climate data scientist analyzing Philippines typhoon data from 2014-2024.

DATASET SUMMARY:
- 132 monthly observations (2014-2024)
- Features: Number_of_Typhoons, ONI (ENSO index), Niño 3.4 SST anomaly, Western Pacific SST anomaly,
  Vertical Wind Shear, Midlevel Humidity, Sea Level Pressure, MJO Phase, Previous month typhoons

KEY STATISTICS:
- Total typhoons (2014-2024): {df['Number_of_Typhoons'].sum()}
- Annual averages by year: {yearly_summary}
- Monthly average typhoon count: {monthly_avg}
- Average by ENSO phase: {enso_avg}
- Correlations with typhoon count: {corr_with_target}
- Peak months: July-October (highest activity)
- Off-season: December-March (lowest activity)
- El Niño years tend to suppress typhoon frequency; La Niña years tend to enhance it
- Vertical wind shear has the strongest negative correlation with typhoon count

Provide expert, data-driven, insightful responses. Reference specific numbers from the data when relevant.
Use a professional but engaging tone. Structure longer answers with clear sections.
"""

    # Preset questions
    st.markdown('<div class="section-tag">QUICK INSIGHTS</div>', unsafe_allow_html=True)
    preset_cols = st.columns(3)
    presets = [
        ("📊 Annual Trends", "What are the key trends in Philippines typhoon frequency from 2014 to 2024? Are typhoons becoming more or less frequent?"),
        ("🌊 ENSO Influence", "How does El Niño and La Niña affect typhoon frequency in the Philippines? What does the data show?"),
        ("🔮 Future Outlook", "Based on climate patterns in the data, what predictions can we make about future typhoon activity in the Philippines?"),
        ("⚡ Peak Season", "What factors drive peak typhoon season (June-November) and how do climate variables interact during this period?"),
        ("🌡️ Climate Drivers", "Which climate variables (SST, wind shear, humidity, etc.) are the strongest predictors of typhoon formation?"),
        ("📅 Worst Years", "What made the most active typhoon years so intense? What climate conditions drove the elevated activity?"),
    ]
    for i, (label, q) in enumerate(presets):
        col = preset_cols[i % 3]
        with col:
            if st.button(label, key=f"preset_{i}"):
                st.session_state["ai_question"] = q

    st.markdown("---")
    st.markdown('<div class="section-tag">ASK THE AI ANALYST</div>', unsafe_allow_html=True)

    question = st.text_area(
        "Your question",
        value=st.session_state.get("ai_question", ""),
        placeholder="e.g. What is the relationship between sea surface temperature and typhoon frequency in El Niño years?",
        height=100,
        label_visibility="collapsed"
    )

    if st.button("🔍 Analyze", use_container_width=False):
        if question.strip():
            with st.spinner("Claude is analyzing the typhoon data..."):
                try:
                    client = anthropic.Anthropic()
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1200,
                        system=DATA_CONTEXT,
                        messages=[{"role": "user", "content": question}]
                    )
                    answer = response.content[0].text
                    st.markdown(f"""
                    <div class="ai-response">
                        <div class="ai-label">🤖 CLAUDE ANALYSIS</div>
                        {answer}
                    </div>""", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"API error: {e}")
        else:
            st.warning("Please enter a question.")

    # Auto-generated insights section
    st.markdown("---")
    st.markdown('<div class="section-tag">AUTO INSIGHTS</div>', unsafe_allow_html=True)

    if st.button("✨ Generate Data Summary Report"):
        with st.spinner("Generating comprehensive report..."):
            try:
                client = anthropic.Anthropic()
                report_prompt = f"""
Generate a comprehensive analytical report on Philippines typhoon data (2014-2024).
Structure it with these sections:
1. Executive Summary (3-4 sentences)
2. Key Findings (5 bullet points with specific numbers)
3. ENSO-Typhoon Relationship Analysis
4. Climate Driver Analysis (which variables matter most and why)
5. Risk Assessment & Seasonal Patterns
6. Recommendations for Early Warning Systems

Be specific with data references and keep the total length to about 600-700 words.
"""
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1500,
                    system=DATA_CONTEXT,
                    messages=[{"role": "user", "content": report_prompt}]
                )
                st.markdown(f"""
                <div class="ai-response">
                    <div class="ai-label">📋 COMPREHENSIVE REPORT — CLAUDE AI</div>
                    {response.content[0].text}
                </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"API error: {e}")