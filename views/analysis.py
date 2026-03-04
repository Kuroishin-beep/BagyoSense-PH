import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.theme import apply_theme, ENSO_COLORS, SEASON_COLORS, MONTH_SHORT


def render(dff: pd.DataFrame):
    st.markdown('<div class="page-title">BagyoSense</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-sub">Philippines Typhoon Intelligence · 2014–2024</div>',
        unsafe_allow_html=True,
    )

    if dff.empty:
        st.warning("No data for current filters — adjust the sidebar.")
        return

    # ── KPIs ─────────────────────────────────────────────────────────────────
    total       = int(dff["Number_of_Typhoons"].sum())
    yearly      = dff.groupby("Year")["Number_of_Typhoons"].sum()
    avg_annual  = yearly.mean()
    peak_month  = dff.groupby("Month_Name")["Number_of_Typhoons"].mean().idxmax()
    worst_year  = int(yearly.idxmax()) if not yearly.empty else "—"
    peak_pct    = (
        dff[dff["Season"] == "Peak (Jun-Nov)"]["Number_of_Typhoons"].sum()
        / max(total, 1) * 100
    )

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-val">{total}</div>
            <div class="kpi-lbl">Total Typhoons</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val">{avg_annual:.1f}</div>
            <div class="kpi-lbl">Avg per Year</div>
        </div>
        <div class="kpi-card warn">
            <div class="kpi-val warn">{peak_month}</div>
            <div class="kpi-lbl">Peak Month</div>
        </div>
        <div class="kpi-card alert">
            <div class="kpi-val alert">{worst_year}</div>
            <div class="kpi-lbl">Most Active Year</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val">{peak_pct:.0f}%</div>
            <div class="kpi-lbl">Peak Season Share</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Annual bar + ENSO donut ───────────────────────────────────────────────
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<div class="section-tag">ANNUAL TYPHOON COUNT + TREND</div>', unsafe_allow_html=True)
        yr_df = dff.groupby("Year")["Number_of_Typhoons"].sum().reset_index()
        trend = np.poly1d(np.polyfit(yr_df["Year"], yr_df["Number_of_Typhoons"], 1))(yr_df["Year"]) \
                if len(yr_df) > 1 else yr_df["Number_of_Typhoons"]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=yr_df["Year"], y=yr_df["Number_of_Typhoons"],
            marker=dict(
                color=yr_df["Number_of_Typhoons"],
                colorscale=[[0,"#0d2240"],[0.5,"#00d4aa"],[1,"#3b82f6"]],
                showscale=False, line=dict(width=0),
            ),
            text=yr_df["Number_of_Typhoons"], textposition="outside",
            textfont=dict(color="#64748b", size=9),
            hovertemplate="<b>%{x}</b>: %{y} typhoons<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=yr_df["Year"], y=trend, mode="lines", name="Trend",
            line=dict(color="#f59e0b", dash="dot", width=2),
            hoverinfo="skip",
        ))
        apply_theme(fig, height=280, show_legend=False,
                    xaxis=dict(tickvals=yr_df["Year"].tolist()),
                    yaxis=dict(range=[0, yr_df["Number_of_Typhoons"].max()*1.3]))
        fig.update_layout(bargap=0.28)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-tag">BY ENSO</div>', unsafe_allow_html=True)
        enso_df = (
            dff.groupby("ENSO_Phase")["Number_of_Typhoons"].sum()
            .reindex(["El Nino","La Nina","Neutral"]).dropna().reset_index()
        )
        fig2 = go.Figure(go.Pie(
            labels=enso_df["ENSO_Phase"], values=enso_df["Number_of_Typhoons"],
            hole=0.6,
            marker=dict(
                colors=[ENSO_COLORS.get(p,"#94a3b8") for p in enso_df["ENSO_Phase"]],
                line=dict(color="#08111f", width=3),
            ),
            textfont=dict(family="IBM Plex Mono", size=9),
            hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>",
        ))
        apply_theme(fig2, height=280, show_legend=True)
        fig2.update_layout(legend=dict(orientation="v", x=0.0, y=0.0, font=dict(size=8)))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Monthly avg + Correlation ─────────────────────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-tag">AVG TYPHOONS BY MONTH</div>', unsafe_allow_html=True)
        m_avg = (dff.groupby("Month")["Number_of_Typhoons"].mean()
                   .reindex(range(1,13)).fillna(0))
        fig3 = go.Figure(go.Bar(
            x=MONTH_SHORT, y=m_avg.values,
            marker=dict(
                color=m_avg.values,
                colorscale=[[0,"#0d2240"],[0.55,"#00d4aa"],[1,"#3b82f6"]],
                showscale=False, line=dict(width=0),
            ),
            hovertemplate="<b>%{x}</b>: %{y:.2f} avg<extra></extra>",
        ))
        apply_theme(fig3, height=255)
        fig3.update_layout(bargap=0.18)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-tag">CLIMATE CORRELATIONS WITH TYPHOON COUNT</div>', unsafe_allow_html=True)
        feat_cols = ["ONI","Nino3.4_SST_anomaly","Western_Pacific_SST",
                     "Vertical_Wind_Shear","Midlevel_Humidity","SeaLevelPressure","Prev_month_typhoons"]
        corr = (dff[feat_cols+["Number_of_Typhoons"]].corr()["Number_of_Typhoons"]
                  .drop("Number_of_Typhoons").sort_values())
        fig4 = go.Figure(go.Bar(
            x=corr.values, y=corr.index, orientation="h",
            marker=dict(color=["#ef4444" if v<0 else "#00d4aa" for v in corr.values],
                        line=dict(width=0)),
            hovertemplate="<b>%{y}</b>: r=%{x:.3f}<extra></extra>",
        ))
        fig4.add_vline(x=0, line_color="#1a3350", line_width=1)
        apply_theme(fig4, height=255, xaxis=dict(range=[-0.75,0.75]))
        st.plotly_chart(fig4, use_container_width=True)

    # ── Heatmap ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-tag">YEAR × MONTH HEATMAP — TYPHOON COUNT</div>', unsafe_allow_html=True)
    pivot = (dff.pivot_table(values="Number_of_Typhoons", index="Year",
                              columns="Month", aggfunc="sum", fill_value=0))
    pivot.columns = [MONTH_SHORT[c-1] for c in pivot.columns]

    fig5 = go.Figure(go.Heatmap(
        z=pivot.values,
        x=list(pivot.columns),
        y=[str(y) for y in pivot.index],
        colorscale=[[0,"#08111f"],[0.2,"#0d2240"],[0.6,"#00d4aa"],[1,"#3b82f6"]],
        showscale=True,
        text=pivot.values, texttemplate="%{text}",
        textfont=dict(size=10, color="#e2e8f0"),
        hovertemplate="<b>%{y} — %{x}</b>: %{z} typhoons<extra></extra>",
        colorbar=dict(tickfont=dict(color="#94a3b8",size=9), outlinecolor="#1a3350"),
    ))
    apply_theme(fig5, height=310)
    st.plotly_chart(fig5, use_container_width=True)

    # ── Seasonal stacked bar ──────────────────────────────────────────────────
    st.markdown('<div class="section-tag">PEAK VS OFF-SEASON SPLIT</div>', unsafe_allow_html=True)
    sea_yr = dff.groupby(["Year","Season"])["Number_of_Typhoons"].sum().reset_index()
    fig6 = go.Figure()
    for season, color in SEASON_COLORS.items():
        sub = sea_yr[sea_yr["Season"]==season]
        fig6.add_trace(go.Bar(
            x=sub["Year"], y=sub["Number_of_Typhoons"],
            name=season, marker_color=color,
            hovertemplate=f"<b>%{{x}}</b> {season}: %{{y}}<extra></extra>",
        ))
    apply_theme(fig6, height=240, show_legend=True)
    fig6.update_layout(barmode="stack", bargap=0.25)
    st.plotly_chart(fig6, use_container_width=True)