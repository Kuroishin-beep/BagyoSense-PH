import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.theme import apply_theme, ENSO_COLORS, COLORS


def render(dff: pd.DataFrame):
    st.markdown('<div class="page-title">Deep Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-sub">Rolling Trends · Cumulative Curves · Climate Drivers</div>',
        unsafe_allow_html=True,
    )

    if dff.empty:
        st.warning("No data for current filters — adjust the sidebar.")
        return

    # Sort by date for time-series analysis
    dff = dff.sort_values("Date").copy()

    # ── Rolling Averages ─────────────────────────────────────────────────────
    st.markdown('<div class="section-tag">ROLLING AVERAGES — TYPHOON COUNT</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dff["Date"], y=dff["Number_of_Typhoons"],
            mode="markers", name="Monthly",
            marker=dict(color="#1e3a5f", size=4, opacity=0.5),
            hovertemplate="<b>%{x|%b %Y}</b>: %{y}<extra></extra>",
        ))
        # 3-month rolling average
        roll3 = dff["Number_of_Typhoons"].rolling(3, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=dff["Date"], y=roll3,
            mode="lines", name="3-month MA",
            line=dict(color="#00d4aa", width=2),
            hovertemplate="3M Avg: %{y:.1f}<extra></extra>",
        ))
        # 12-month rolling average
        roll12 = dff["Number_of_Typhoons"].rolling(12, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=dff["Date"], y=roll12,
            mode="lines", name="12-month MA",
            line=dict(color="#f59e0b", width=2.5, dash="dash"),
            hovertemplate="12M Avg: %{y:.1f}<extra></extra>",
        ))
        apply_theme(fig, height=300, show_legend=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-tag">STATISTICS</div>', unsafe_allow_html=True)
        avg_all = dff["Number_of_Typhoons"].mean()
        std_all = dff["Number_of_Typhoons"].std()
        max_val = int(dff["Number_of_Typhoons"].max())
        max_date = dff.loc[dff["Number_of_Typhoons"].idxmax(), "Date"]
        st.markdown(f"""
        <div class="insight-box">
            <div style="font-family:IBM Plex Mono;font-size:0.6rem;color:#94a3b8;
                        text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem">
                Monthly Summary</div>
            <span class="pred-chip">Mean: {avg_all:.2f}</span>
            <span class="pred-chip">Std: {std_all:.2f}</span>
            <span class="pred-chip">Max: {max_val}</span>
            <div style="font-family:IBM Plex Mono;font-size:0.55rem;color:#64748b;
                        margin-top:0.5rem">
                Peak: {max_date.strftime('%b %Y') if hasattr(max_date, 'strftime') else max_date}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Cumulative Typhoon Curves by Year ────────────────────────────────────
    st.markdown('<div class="section-tag">CUMULATIVE TYPHOONS BY YEAR</div>',
                unsafe_allow_html=True)

    col3, col4 = st.columns([3, 1])
    with col3:
        fig2 = go.Figure()
        palette = ["#00d4aa", "#3b82f6", "#a855f7", "#f59e0b", "#ef4444",
                    "#10b981", "#06b6d4", "#f43f5e", "#8b5cf6", "#14b8a6", "#eab308"]
        years = sorted(dff["Year"].unique())
        for i, yr in enumerate(years):
            yr_data = dff[dff["Year"] == yr].sort_values("Month")
            cumsum = yr_data["Number_of_Typhoons"].cumsum()
            fig2.add_trace(go.Scatter(
                x=yr_data["Month"], y=cumsum,
                mode="lines+markers", name=str(yr),
                line=dict(color=palette[i % len(palette)], width=2),
                marker=dict(size=4),
                hovertemplate=f"<b>{yr}</b> Month %{{x}}: %{{y}} cumulative<extra></extra>",
            ))
        apply_theme(fig2, height=320, show_legend=True,
                    xaxis=dict(title="Month", tickvals=list(range(1, 13)),
                               ticktext=["J","F","M","A","M","J","J","A","S","O","N","D"]),
                    yaxis=dict(title="Cumulative Count"))
        fig2.update_layout(legend=dict(
            orientation="v", x=1.02, y=1, font=dict(size=9),
            bgcolor="rgba(0,0,0,0)"
        ))
        st.plotly_chart(fig2, use_container_width=True)

    with col4:
        st.markdown('<div class="section-tag">ANNUAL TOTALS</div>', unsafe_allow_html=True)
        annual = dff.groupby("Year")["Number_of_Typhoons"].sum()
        yoy_change = annual.pct_change() * 100
        for yr in years[-5:]:  # show last 5 years
            total = int(annual.get(yr, 0))
            change = yoy_change.get(yr, 0)
            if pd.notna(change):
                color = "#00d4aa" if change >= 0 else "#ef4444"
                arrow = "▲" if change >= 0 else "▼"
                change_str = f'<span style="color:{color};font-size:0.65rem">{arrow} {abs(change):.0f}%</span>'
            else:
                change_str = ""
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:4px 0;border-bottom:1px solid #1e3a5f">
                <span style="font-family:IBM Plex Mono;font-size:0.75rem;color:#94a3b8">{yr}</span>
                <span>
                    <span style="font-family:Syne;font-weight:800;color:#e2e8f0;font-size:0.9rem">{total}</span>
                    {change_str}
                </span>
            </div>
            """, unsafe_allow_html=True)

    # ── Scatter Matrix — Climate Variables vs Typhoon Count ──────────────────
    st.markdown('<div class="section-tag">CLIMATE DRIVERS — SCATTER ANALYSIS</div>',
                unsafe_allow_html=True)

    scatter_vars = [
        ("ONI", "ONI Index", "#3b82f6"),
        ("Vertical_Wind_Shear", "Wind Shear", "#ef4444"),
        ("Midlevel_Humidity", "Humidity (%)", "#00d4aa"),
        ("Western_Pacific_SST", "W. Pacific SST", "#a855f7"),
    ]

    cols = st.columns(len(scatter_vars))
    for i, (col_name, label, color) in enumerate(scatter_vars):
        with cols[i]:
            fig_s = go.Figure(go.Scatter(
                x=dff[col_name], y=dff["Number_of_Typhoons"],
                mode="markers",
                marker=dict(color=color, size=5, opacity=0.7,
                            line=dict(width=0.5, color="#08111f")),
                hovertemplate=f"<b>{label}</b>: %{{x:.2f}}<br>Typhoons: %{{y}}<extra></extra>",
            ))
            # Add trendline
            if len(dff) > 2:
                z = np.polyfit(dff[col_name], dff["Number_of_Typhoons"], 1)
                p = np.poly1d(z)
                x_range = np.linspace(dff[col_name].min(), dff[col_name].max(), 50)
                fig_s.add_trace(go.Scatter(
                    x=x_range, y=p(x_range),
                    mode="lines", showlegend=False,
                    line=dict(color=color, width=1.5, dash="dash"),
                ))
            corr_val = dff[col_name].corr(dff["Number_of_Typhoons"])
            apply_theme(fig_s, height=220,
                        xaxis=dict(title=label),
                        yaxis=dict(title="Typhoons"))
            fig_s.update_layout(
                title=dict(text=f"r = {corr_val:.3f}",
                           font=dict(size=10, color="#94a3b8"),
                           x=0.5, y=0.95),
            )
            st.plotly_chart(fig_s, use_container_width=True)

    # ── ENSO Phase Comparison — Box Plots ────────────────────────────────────
    st.markdown('<div class="section-tag">ENSO PHASE COMPARISON — DISTRIBUTION</div>',
                unsafe_allow_html=True)

    col5, col6 = st.columns(2)

    with col5:
        fig_box = go.Figure()
        for phase in ["La Nina", "Neutral", "El Nino"]:
            phase_data = dff[dff["ENSO_Phase"] == phase]["Number_of_Typhoons"]
            fig_box.add_trace(go.Box(
                y=phase_data, name=phase,
                marker_color=ENSO_COLORS.get(phase, "#94a3b8"),
                boxmean="sd",
                hovertemplate=f"<b>{phase}</b><br>%{{y}} typhoons<extra></extra>",
            ))
        apply_theme(fig_box, height=280, show_legend=False,
                    yaxis=dict(title="Typhoons / Month"))
        fig_box.update_layout(title=dict(
            text="Monthly Typhoon Distribution by ENSO Phase",
            font=dict(size=11, color="#94a3b8"), x=0.5,
        ))
        st.plotly_chart(fig_box, use_container_width=True)

    with col6:
        # ENSO phase monthly pattern
        fig_enso_m = go.Figure()
        month_labels = ["J","F","M","A","M","J","J","A","S","O","N","D"]
        for phase in ["La Nina", "Neutral", "El Nino"]:
            phase_data = dff[dff["ENSO_Phase"] == phase]
            monthly_avg = phase_data.groupby("Month")["Number_of_Typhoons"].mean().reindex(range(1,13)).fillna(0)
            fig_enso_m.add_trace(go.Scatter(
                x=month_labels, y=monthly_avg.values,
                mode="lines+markers", name=phase,
                line=dict(color=ENSO_COLORS.get(phase, "#94a3b8"), width=2),
                marker=dict(size=5),
                hovertemplate=f"<b>{phase}</b> %{{x}}: %{{y:.2f}} avg<extra></extra>",
            ))
        apply_theme(fig_enso_m, height=280, show_legend=True,
                    yaxis=dict(title="Avg Typhoons"))
        fig_enso_m.update_layout(title=dict(
            text="Monthly Pattern by ENSO Phase",
            font=dict(size=11, color="#94a3b8"), x=0.5,
        ))
        st.plotly_chart(fig_enso_m, use_container_width=True)

    # ── Year-over-Year Change ────────────────────────────────────────────────
    st.markdown('<div class="section-tag">YEAR-OVER-YEAR CHANGE</div>',
                unsafe_allow_html=True)

    annual_totals = dff.groupby("Year")["Number_of_Typhoons"].sum()
    yoy = annual_totals.diff().dropna()

    if len(yoy) > 0:
        fig_yoy = go.Figure(go.Bar(
            x=[str(int(y)) for y in yoy.index],
            y=yoy.values,
            marker=dict(
                color=["#00d4aa" if v >= 0 else "#ef4444" for v in yoy.values],
                line=dict(width=0),
            ),
            text=[f"+{int(v)}" if v >= 0 else str(int(v)) for v in yoy.values],
            textposition="outside",
            textfont=dict(color="#94a3b8", size=10),
            hovertemplate="<b>%{x}</b>: %{y:+d} typhoons vs prev year<extra></extra>",
        ))
        apply_theme(fig_yoy, height=240,
                    yaxis=dict(title="Change from Previous Year"))
        fig_yoy.add_hline(y=0, line_color="#1e3a5f", line_width=1)
        fig_yoy.update_layout(bargap=0.3)
        st.plotly_chart(fig_yoy, use_container_width=True)

    # ── Climate Variable Correlation Heatmap ─────────────────────────────────
    st.markdown('<div class="section-tag">FULL CORRELATION MATRIX</div>',
                unsafe_allow_html=True)

    corr_cols = ["Number_of_Typhoons", "ONI", "Nino3.4_SST_anomaly",
                 "Western_Pacific_SST", "Vertical_Wind_Shear",
                 "Midlevel_Humidity", "SeaLevelPressure", "MJO_Phase",
                 "Prev_month_typhoons"]
    corr_labels = ["Typhoons", "ONI", "Niño3.4", "W.Pac SST",
                   "Wind Shear", "Humidity", "SLP", "MJO", "Prev Month"]

    corr_matrix = dff[corr_cols].corr()

    fig_corr = go.Figure(go.Heatmap(
        z=corr_matrix.values,
        x=corr_labels, y=corr_labels,
        colorscale=[[0, "#ef4444"], [0.5, "#08111f"], [1, "#00d4aa"]],
        zmid=0, showscale=True,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=9, color="#e2e8f0"),
        hovertemplate="<b>%{x}</b> × <b>%{y}</b><br>r = %{z:.3f}<extra></extra>",
        colorbar=dict(tickfont=dict(color="#94a3b8", size=9), outlinecolor="#1a3350"),
    ))
    apply_theme(fig_corr, height=400)
    fig_corr.update_layout(
        xaxis=dict(tickangle=-45),
        margin=dict(l=10, r=10, t=30, b=80),
    )
    st.plotly_chart(fig_corr, use_container_width=True)