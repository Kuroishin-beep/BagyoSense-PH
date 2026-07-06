import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import plotly.graph_objects as go

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from utils.theme import apply_theme

FEATURES = ["Month", "ONI", "Nino3.4_SST_anomaly", "Western_Pacific_SST",
             "Vertical_Wind_Shear", "Midlevel_Humidity", "SeaLevelPressure",
             "MJO_Phase", "Prev_month_typhoons"]
TARGET = "Number_of_Typhoons"

MONTH_FULL = {1: "January", 2: "February", 3: "March", 4: "April",
              5: "May", 6: "June", 7: "July", 8: "August",
              9: "September", 10: "October", 11: "November", 12: "December"}

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")


def _pretrained_exists() -> bool:
    """Check whether pretrained models have been saved to disk."""
    return (
        os.path.isfile(os.path.join(MODEL_DIR, "all_models.joblib"))
        and os.path.isfile(os.path.join(MODEL_DIR, "scaler.joblib"))
        and os.path.isfile(os.path.join(MODEL_DIR, "metrics.json"))
    )


@st.cache_resource(show_spinner=False)
def load_pretrained():
    """Load pretrained models, scaler, and metrics from disk."""
    import joblib

    models_dict = joblib.load(os.path.join(MODEL_DIR, "all_models.joblib"))
    scaler      = joblib.load(os.path.join(MODEL_DIR, "scaler.joblib"))
    with open(os.path.join(MODEL_DIR, "metrics.json")) as f:
        metrics = json.load(f)

    best_name = metrics.pop("_best_model")
    metrics.pop("_features", None)
    metrics.pop("_target", None)

    return models_dict, scaler, metrics, best_name


@st.cache_resource(show_spinner=False)
def train_models_live(_df: pd.DataFrame):
    """Fallback: train models in-session if no pretrained models exist."""
    X = _df[FEATURES]
    y = _df[TARGET]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    sc = StandardScaler()
    Xtr_sc = sc.fit_transform(X_tr)
    Xte_sc = sc.transform(X_te)

    specs = {
        "Random Forest":     RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, max_depth=4, random_state=42),
        "Linear Regression": LinearRegression(),
    }

    # Try to import XGBoost
    try:
        from xgboost import XGBRegressor
        specs["XGBoost"] = XGBRegressor(
            n_estimators=200, max_depth=4, learning_rate=0.1,
            random_state=42, verbosity=0,
        )
        # reorder so XGBoost is first
        specs = {"XGBoost": specs.pop("XGBoost"), **specs}
    except ImportError:
        pass

    models_dict = {}
    metrics = {}

    for name, model in specs.items():
        use_scaled = name == "Linear Regression"
        X_fit = Xtr_sc if use_scaled else X_tr
        X_eval = Xte_sc if use_scaled else X_te

        model.fit(X_fit, y_tr)
        raw = model.predict(X_eval)
        preds = np.clip(np.round(raw), 0, None)

        r2   = r2_score(y_te, preds)
        rmse = np.sqrt(mean_squared_error(y_te, preds))
        mae  = mean_absolute_error(y_te, preds)

        models_dict[name] = {"model": model, "uses_scaler": use_scaled}
        metrics[name] = {
            "test_r2": round(float(r2), 4),
            "rmse":    round(float(rmse), 4),
            "mae":     round(float(mae), 4),
        }

    best_name = max(metrics, key=lambda k: metrics[k]["test_r2"])
    return models_dict, sc, metrics, best_name


def render(df: pd.DataFrame):
    st.markdown('<div class="page-title">ML Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Ensemble Machine Learning · Typhoon Forecasting</div>',
                unsafe_allow_html=True)

    # ── Load or train models ─────────────────────────────────────────────────
    if _pretrained_exists():
        with st.spinner("Loading pretrained models…"):
            models_dict, scaler, metrics, best_name = load_pretrained()
        st.markdown("""
        <div class="insight-box" style="border-left-color:#00d4aa;padding:0.7rem 1rem">
            <span style="font-family:IBM Plex Mono;font-size:0.6rem;color:#00d4aa;
                         text-transform:uppercase;letter-spacing:0.1em">
                ✓ Pretrained models loaded from disk — instant startup
            </span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No pretrained models found. Run `python train_model.py` first for best results. "
                   "Falling back to live training…")
        with st.spinner("Training models…"):
            models_dict, scaler, metrics, best_name = train_models_live(df)

    # ── Evaluate on current data for display ─────────────────────────────────
    X = df[FEATURES]
    y = df[TARGET]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
    X_te_sc = scaler.transform(X_te)

    results = {}
    for name, mdata in models_dict.items():
        model = mdata["model"]
        use_sc = mdata["uses_scaler"]
        raw = model.predict(X_te_sc if use_sc else X_te)
        preds = np.clip(np.round(raw), 0, None)
        results[name] = {
            "preds":  preds,
            "y_test": y_te.values,
            "r2":     r2_score(y_te, preds),
            "rmse":   np.sqrt(mean_squared_error(y_te, preds)),
            "mae":    mean_absolute_error(y_te, preds),
            "model":  model,
        }
        # Merge saved metrics (cv_r2 etc.) if available
        if name in metrics:
            results[name]["cv_r2"] = metrics[name].get("cv_r2")

    # ── Model cards ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-tag">MODEL PERFORMANCE</div>', unsafe_allow_html=True)
    n_models = len(results)
    cols = st.columns(min(n_models, 4))
    for i, (name, res) in enumerate(results.items()):
        crown = "🏆  " if name == best_name else ""
        r2c = "#00d4aa" if res["r2"] > 0.4 else ("#f59e0b" if res["r2"] > 0.2 else "#ef4444")
        cv_chip = ""
        if res.get("cv_r2") is not None:
            cv_chip = f'<span class="pred-chip" style="color:#a855f7">CV R² {res["cv_r2"]:.3f}</span>'
        with cols[i % len(cols)]:
            st.markdown(f"""
            <div class="insight-box">
                <div style="font-family:Syne;font-weight:800;font-size:0.9rem;
                            color:#e2e8f0;margin-bottom:0.6rem">{crown}{name}</div>
                <span class="pred-chip" style="color:{r2c}">R² {res['r2']:.3f}</span>
                {cv_chip}
                <span class="pred-chip">RMSE {res['rmse']:.2f}</span>
                <span class="pred-chip">MAE {res['mae']:.2f}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Actual vs Predicted + Feature Importance ─────────────────────────────
    col1, col2 = st.columns(2)
    best = results[best_name]

    with col1:
        st.markdown(f'<div class="section-tag">ACTUAL vs PREDICTED — {best_name}</div>',
                    unsafe_allow_html=True)
        idx = list(range(len(best["y_test"])))
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=idx, y=best["y_test"].tolist(), mode="lines+markers",
            name="Actual", line=dict(color="#00d4aa", width=2),
            marker=dict(size=5),
        ))
        fig.add_trace(go.Scatter(
            x=idx, y=best["preds"].tolist(), mode="lines+markers",
            name="Predicted", line=dict(color="#f59e0b", dash="dash", width=2),
            marker=dict(size=5, symbol="diamond"),
        ))
        apply_theme(fig, height=290, show_legend=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-tag">FEATURE IMPORTANCE</div>',
                    unsafe_allow_html=True)
        # Get feature importance from the best model that supports it
        fi_model = best["model"]
        fi_values = None
        if hasattr(fi_model, "feature_importances_"):
            fi_values = fi_model.feature_importances_
        elif "Random Forest" in results and hasattr(results["Random Forest"]["model"], "feature_importances_"):
            fi_model = results["Random Forest"]["model"]
            fi_values = fi_model.feature_importances_

        if fi_values is not None:
            fi = pd.DataFrame({"Feature": FEATURES, "Importance": fi_values}).sort_values("Importance")
            fig2 = go.Figure(go.Bar(
                x=fi["Importance"], y=fi["Feature"], orientation="h",
                marker=dict(color=fi["Importance"],
                            colorscale=[[0, "#1a3350"], [1, "#00d4aa"]],
                            showscale=False, line=dict(width=0)),
                hovertemplate="<b>%{y}</b>: %{x:.3f}<extra></extra>",
            ))
            apply_theme(fig2, height=290)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Feature importance not available for Linear Regression.")

    # ── Residuals ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-tag">RESIDUAL ANALYSIS — BEST MODEL</div>',
                unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    residuals = best["y_test"] - best["preds"]

    with col3:
        fig3 = go.Figure(go.Scatter(
            x=best["preds"], y=residuals, mode="markers",
            marker=dict(color=np.abs(residuals),
                        colorscale=[[0, "#00d4aa"], [1, "#ef4444"]],
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
            marker=dict(color="#3b82f6", opacity=0.8,
                        line=dict(color="#08111f", width=0.5)),
            hovertemplate="Residual:%{x:.1f} Count:%{y}<extra></extra>",
        ))
        apply_theme(fig4, height=240,
                    xaxis=dict(title="Residual"),
                    yaxis=dict(title="Count"))
        st.plotly_chart(fig4, use_container_width=True)

    # ── Interactive predictor ────────────────────────────────────────────────
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

    arr = np.array([[p_month, p_oni, p_nino, p_sst, p_shear, p_hum, p_slp, p_mjo, p_prev]])
    arr_sc = scaler.transform(arr)

    # Predict with all available models
    predictions = {}
    for name, mdata in models_dict.items():
        model = mdata["model"]
        use_sc = mdata["uses_scaler"]
        pred = int(np.clip(round(model.predict(arr_sc if use_sc else arr)[0]), 0, 12))
        predictions[name] = pred

    ens = round(sum(predictions.values()) / len(predictions), 1)

    enso = "El Nino" if p_oni >= 0.5 else ("La Nina" if p_oni <= -0.5 else "Neutral ENSO")
    risk_cls = "alert" if ens >= 4 else ("warn" if ens >= 2 else "")
    risk_lbl = "HIGH RISK" if ens >= 4 else ("MODERATE" if ens >= 2 else "LOW ACTIVITY")

    # Build prediction chips
    chip_html = ""
    for name, pred in predictions.items():
        short = {"XGBoost": "XGB", "Random Forest": "RF",
                 "Gradient Boosting": "GB", "Linear Regression": "LR"}.get(name, name[:3])
        chip_html += f'<span class="pred-chip">{short}: {pred}</span>\n'

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
                {chip_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)