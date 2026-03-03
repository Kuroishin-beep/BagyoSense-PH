import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from utils.theme import apply_theme

FEATURES = ["Month","ONI","Nino3.4_SST_anomaly","Western_Pacific_SST",
            "Vertical_Wind_Shear","Midlevel_Humidity","SeaLevelPressure",
            "MJO_Phase","Prev_month_typhoons"]
TARGET = "Number_of_Typhoons"

MONTH_FULL = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
              7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}


@st.cache_data(show_spinner=False)
def train_models(_df: pd.DataFrame):
    X = _df[FEATURES]; y = _df[TARGET]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
    sc = StandardScaler()
    Xtr_sc = sc.fit_transform(X_tr); Xte_sc = sc.transform(X_te)

    specs = {
        "Random Forest":     RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, max_depth=4, random_state=42),
        "Linear Regression": LinearRegression(),
    }
    results = {}
    for name, model in specs.items():
        if name == "Linear Regression":
            model.fit(Xtr_sc, y_tr); raw = model.predict(Xte_sc)
        else:
            model.fit(X_tr, y_tr); raw = model.predict(X_te)
        preds = np.clip(np.round(raw), 0, None)
        results[name] = dict(model=model, preds=preds, y_test=y_te.values,
                             r2=r2_score(y_te,preds),
                             rmse=np.sqrt(mean_squared_error(y_te,preds)),
                             mae=mean_absolute_error(y_te,preds))
    return results, sc


def render(df: pd.DataFrame):
    st.markdown('<div class="page-title">ML Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Ensemble Machine Learning · Typhoon Forecasting</div>', unsafe_allow_html=True)

    with st.spinner("Training models…"):
        results, scaler = train_models(df)

    best_name = max(results, key=lambda k: results[k]["r2"])

    # ── Model cards ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-tag">MODEL PERFORMANCE</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, (name, res) in enumerate(results.items()):
        crown = "🏆 " if name == best_name else ""
        r2c = "#00d4aa" if res["r2"]>0.4 else ("#f59e0b" if res["r2"]>0.2 else "#ef4444")
        with cols[i]:
            st.markdown(f"""
            <div class="insight-box">
                <div style="font-family:Syne;font-weight:800;font-size:0.9rem;
                            color:#e2e8f0;margin-bottom:0.6rem">{crown}{name}</div>
                <span class="pred-chip" style="color:{r2c}">R² {res['r2']:.3f}</span>
                <span class="pred-chip">RMSE {res['rmse']:.2f}</span>
                <span class="pred-chip">MAE {res['mae']:.2f}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Actual vs Predicted + Feature Importance ──────────────────────────────
    col1, col2 = st.columns(2)
    best = results[best_name]

    with col1:
        st.markdown(f'<div class="section-tag">ACTUAL vs PREDICTED — {best_name}</div>', unsafe_allow_html=True)
        idx = list(range(len(best["y_test"])))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=idx, y=best["y_test"].tolist(), mode="lines+markers",
                                  name="Actual", line=dict(color="#00d4aa",width=2), marker=dict(size=5)))
        fig.add_trace(go.Scatter(x=idx, y=best["preds"].tolist(), mode="lines+markers",
                                  name="Predicted", line=dict(color="#f59e0b",dash="dash",width=2),
                                  marker=dict(size=5,symbol="diamond")))
        apply_theme(fig, height=290, show_legend=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-tag">FEATURE IMPORTANCE (RANDOM FOREST)</div>', unsafe_allow_html=True)
        rf = results["Random Forest"]["model"]
        fi = pd.DataFrame({"Feature":FEATURES,"Importance":rf.feature_importances_}).sort_values("Importance")
        fig2 = go.Figure(go.Bar(
            x=fi["Importance"], y=fi["Feature"], orientation="h",
            marker=dict(color=fi["Importance"],
                        colorscale=[[0,"#1a3350"],[1,"#00d4aa"]],
                        showscale=False, line=dict(width=0)),
            hovertemplate="<b>%{y}</b>: %{x:.3f}<extra></extra>",
        ))
        apply_theme(fig2, height=290)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Residuals ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-tag">RESIDUAL ANALYSIS — BEST MODEL</div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    residuals = best["y_test"] - best["preds"]

    with col3:
        fig3 = go.Figure(go.Scatter(
            x=best["preds"], y=residuals, mode="markers",
            marker=dict(color=np.abs(residuals),
                        colorscale=[[0,"#00d4aa"],[1,"#ef4444"]],
                        size=7, opacity=0.8, showscale=False),
            hovertemplate="Pred:%{x:.1f} Residual:%{y:.1f}<extra></extra>",
        ))
        fig3.add_hline(y=0, line_color="#1a3350", line_width=1)
        apply_theme(fig3, height=240,
                    xaxis=dict(title="Predicted"),
                    yaxis=dict(title="Residual"))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = go.Figure(go.Histogram(
            x=residuals, nbinsx=15,
            marker=dict(color="#3b82f6", opacity=0.8, line=dict(color="#08111f",width=0.5)),
            hovertemplate="Residual:%{x:.1f} Count:%{y}<extra></extra>",
        ))
        apply_theme(fig4, height=240, xaxis=dict(title="Residual"), yaxis=dict(title="Count"))
        st.plotly_chart(fig4, use_container_width=True)

    # ── Interactive predictor ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-tag">INTERACTIVE PREDICTOR</div>', unsafe_allow_html=True)
    st.markdown("Adjust the parameters below for a real-time ensemble forecast.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Temporal**")
        p_month = st.slider("Month", 1, 12, 8)
        p_prev  = st.slider("Prev Month Typhoons", 0, 8, 1)
        p_mjo   = st.slider("MJO Phase", 0, 8, 4)
    with c2:
        st.markdown("**ENSO / Ocean**")
        p_oni   = st.slider("ONI Index", -2.5, 2.5, 0.0, 0.05)
        p_nino  = st.slider("Nino 3.4 SST Anomaly", -2.5, 2.5, 0.0, 0.05)
        p_sst   = st.slider("W. Pacific SST Anomaly", -1.5, 1.5, 0.0, 0.05)
    with c3:
        st.markdown("**Atmospheric**")
        p_shear = st.slider("Vertical Wind Shear", 5.0, 16.0, 8.0, 0.1)
        p_hum   = st.slider("Midlevel Humidity (%)", 45.0, 80.0, 68.0, 0.5)
        p_slp   = st.slider("Sea Level Pressure (hPa)", 1002.0, 1013.0, 1005.0, 0.1)

    arr = np.array([[p_month,p_oni,p_nino,p_sst,p_shear,p_hum,p_slp,p_mjo,p_prev]])
    arr_sc = scaler.transform(arr)

    rf_p  = int(np.clip(round(results["Random Forest"]["model"].predict(arr)[0]),0,12))
    gb_p  = int(np.clip(round(results["Gradient Boosting"]["model"].predict(arr)[0]),0,12))
    lr_p  = int(np.clip(round(results["Linear Regression"]["model"].predict(arr_sc)[0]),0,12))
    ens   = round((rf_p+gb_p+lr_p)/3, 1)

    enso  = "El Nino" if p_oni>=0.5 else ("La Nina" if p_oni<=-0.5 else "Neutral ENSO")
    risk_cls  = "alert" if ens>=4 else ("warn" if ens>=2 else "")
    risk_lbl  = "HIGH RISK" if ens>=4 else ("MODERATE" if ens>=2 else "LOW ACTIVITY")

    st.markdown(f"""
    <div class="insight-box {risk_cls}" style="margin-top:1rem">
        <div style="font-family:Syne;font-weight:800;font-size:1rem;
                    color:#e2e8f0;margin-bottom:0.8rem">
            {MONTH_FULL[p_month]} · {enso} · {risk_lbl}
        </div>
        <div style="display:flex;gap:2rem;align-items:center;flex-wrap:wrap">
            <div>
                <div style="font-family:IBM Plex Mono;font-size:0.58rem;color:#94a3b8;
                            text-transform:uppercase;letter-spacing:0.1em">Ensemble</div>
                <div style="font-family:Syne;font-size:2.8rem;font-weight:800;
                            color:#00d4aa;line-height:1">{ens}</div>
                <div style="font-family:IBM Plex Mono;font-size:0.58rem;color:#94a3b8">
                    TYPHOONS EXPECTED
                </div>
            </div>
            <div>
                <span class="pred-chip">RF: {rf_p}</span>
                <span class="pred-chip">GB: {gb_p}</span>
                <span class="pred-chip">LR: {lr_p}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)