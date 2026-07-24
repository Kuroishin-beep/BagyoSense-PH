"""
BagyoSense-PH — Training & Export Pipeline
==========================================
One script that trains the typhoon models *honestly* and exports everything the
Next.js app needs. It replaces the older scripts that (a) scored models on their
own training data and (b) hand-typed "predictions" into the dataset.

What "honest" means here:
  * The data is temporal, so we never let the model peek at the future. Model
    selection uses TimeSeriesSplit cross-validation, and final numbers come from
    a chronological hold-out (the most recent ~18 months), never from the rows
    the model trained on.
  * We report a plain seasonal-average baseline alongside the models, so a reader
    can see whether the ML actually beats "just use the monthly average."
  * The forward 12-month forecast is produced by the trained model under a stated
    climate scenario — it is clearly flagged as illustrative, not an official
    PAGASA/NOAA forecast.

Usage:
    python train_model.py

Outputs:
    public/data.json    history (predicted:false) + 12-month forecast (predicted:true)
    public/model.json   linear coefficients + honest metrics + feature importance
    models/*.joblib     fitted estimators + scaler (local convenience)
"""

import os
import sys
import json
import warnings
import numpy as np

# Windows consoles default to cp1252; make Unicode (→, ²) printable.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import pandas as pd
import joblib

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.inspection import permutation_importance

warnings.filterwarnings("ignore", category=UserWarning)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
MODEL_DIR  = os.path.join(BASE_DIR, "models")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

# Prefer the most complete dataset available.
DATA_CANDIDATES = [
    "philippines_typhoon_monthly_latest.csv",
    "philippines_typhoon_monthly_2014_2025.csv",
    "philippines_typhoon_monthly_2014_2024.csv",
]

FEATURES = [
    "Month", "ONI", "Nino3.4_SST_anomaly", "Western_Pacific_SST",
    "Vertical_Wind_Shear", "Midlevel_Humidity", "SeaLevelPressure",
    "MJO_Phase", "Prev_month_typhoons",
]
# Friendly keys used by the frontend, in the SAME order as FEATURES.
FEATURE_KEYS = [
    "month", "oni", "nino34", "wPacSST",
    "windShear", "humidity", "slp", "mjoPhase", "prevMonth",
]
TARGET = "Number_of_Typhoons"

MONTH_SHORT = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}

HOLDOUT_MONTHS = 18   # most recent months reserved for honest evaluation
CV_SPLITS = 5

# ── Forward climate scenario (illustrative) ───────────────────────────────────
# A stated "developing El Niño" scenario for the 12 months after the dataset ends.
# These are assumed climate drivers, not observations — the model turns them into
# a typhoon-count forecast. Change these to explore other scenarios.
# [Year, Month, ONI, Nino34, WPacSST, WindShear, Humidity, SLP, MJO]
FORECAST_SCENARIO = [
    [2026,  7, 0.90,  0.95, -0.10,  8.8, 69.0, 1005.0, 4],
    [2026,  8, 1.10,  1.15, -0.20,  8.5, 68.5, 1004.5, 5],
    [2026,  9, 1.30,  1.35, -0.30,  8.8, 67.0, 1004.0, 3],
    [2026, 10, 1.50,  1.55, -0.40,  9.5, 62.0, 1005.0, 5],
    [2026, 11, 1.60,  1.65, -0.30, 10.0, 63.0, 1007.5, 4],
    [2026, 12, 1.50,  1.55, -0.20, 12.0, 55.0, 1009.5, 6],
    [2027,  1, 1.30,  1.35, -0.10, 12.5, 56.0, 1009.8, 4],
    [2027,  2, 1.00,  1.05,  0.00, 12.8, 55.0, 1010.0, 5],
    [2027,  3, 0.70,  0.75,  0.10, 13.0, 52.5, 1009.5, 3],
    [2027,  4, 0.40,  0.45,  0.20, 10.8, 59.0, 1008.2, 2],
    [2027,  5, 0.20,  0.25,  0.30, 11.2, 60.0, 1007.8, 4],
    [2027,  6, 0.00,  0.05,  0.40,  8.5, 68.0, 1006.0, 5],
]


# ── Helpers ───────────────────────────────────────────────────────────────────
def enso_phase(oni: float) -> str:
    if oni >= 0.5:
        return "El Nino"
    if oni <= -0.5:
        return "La Nina"
    return "Neutral"


def season(month: int) -> str:
    return "Peak" if 6 <= month <= 11 else "Off-Season"


def load_data() -> pd.DataFrame:
    for name in DATA_CANDIDATES:
        path = os.path.join(DATASET_DIR, name)
        if os.path.exists(path):
            df = pd.read_csv(path)
            df = df.sort_values(["Year", "Month"]).reset_index(drop=True)
            print(f"[data] {name}: {len(df)} rows, "
                  f"{df.Year.min()}-{df.Month.iloc[0]:02d} → {df.Year.max()}-{df.Month.iloc[-1]:02d}")
            return df
    raise FileNotFoundError("No dataset CSV found in dataset/")


def build_models():
    """name -> (estimator, needs_scaling, is_linear)."""
    return {
        "Linear Regression": (LinearRegression(), True, True),
        "Ridge": (Ridge(alpha=1.0), True, True),
        "Random Forest": (
            RandomForestRegressor(
                n_estimators=300, max_depth=5, min_samples_leaf=2,
                random_state=42, n_jobs=-1),
            False, False),
        "Gradient Boosting": (
            GradientBoostingRegressor(
                n_estimators=200, max_depth=3, learning_rate=0.05,
                random_state=42),
            False, False),
    }


def scores(y_true, y_pred) -> dict:
    y_pred = np.clip(np.round(y_pred), 0, None)
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
    }


def seasonal_baseline(train: pd.DataFrame, months: np.ndarray) -> np.ndarray:
    """Predict each month with its historical average from the training years."""
    by_month = train.groupby("Month")[TARGET].mean()
    overall = train[TARGET].mean()
    return np.array([by_month.get(int(m), overall) for m in months])


# ── Train + evaluate ──────────────────────────────────────────────────────────
def train(df: pd.DataFrame):
    X = df[FEATURES].to_numpy(dtype=float)
    y = df[TARGET].to_numpy(dtype=float)
    n = len(df)
    split = n - HOLDOUT_MONTHS

    X_tr, X_te = X[:split], X[split:]
    y_tr, y_te = y[:split], y[split:]
    df_tr, df_te = df.iloc[:split], df.iloc[split:]

    print(f"\n[split] train = {len(X_tr)} months, hold-out = {len(X_te)} months "
          f"(chronological, no shuffling)\n")

    scaler = StandardScaler().fit(X_tr)
    X_tr_sc, X_te_sc = scaler.transform(X_tr), scaler.transform(X_te)

    tscv = TimeSeriesSplit(n_splits=CV_SPLITS)
    results = {}
    linear_fits = {}

    for name, (est, needs_scaling, is_linear) in build_models().items():
        Xtr_use = X_tr_sc if needs_scaling else X_tr
        Xte_use = X_te_sc if needs_scaling else X_te

        # Honest CV on the training window only (expanding time-series folds).
        cv_r2, cv_rmse = [], []
        for tr_idx, va_idx in tscv.split(Xtr_use):
            est.fit(Xtr_use[tr_idx], y_tr[tr_idx])
            p = est.predict(Xtr_use[va_idx])
            s = scores(y_tr[va_idx], p)
            cv_r2.append(s["r2"]); cv_rmse.append(s["rmse"])

        # Refit on the full training window, evaluate on the untouched hold-out.
        est.fit(Xtr_use, y_tr)
        hold = scores(y_te, est.predict(Xte_use))

        results[name] = {
            "cvR2": round(float(np.mean(cv_r2)), 4),
            "cvRmse": round(float(np.mean(cv_rmse)), 4),
            "testR2": round(hold["r2"], 4),
            "rmse": round(hold["rmse"], 4),
            "mae": round(hold["mae"], 4),
            "isLinear": is_linear,
            "needsScaling": needs_scaling,
        }
        if is_linear:
            linear_fits[name] = est
        print(f"  {name:<18} CV R²={results[name]['cvR2']:+.3f} "
              f"CV RMSE={results[name]['cvRmse']:.3f} | "
              f"hold-out R²={results[name]['testR2']:+.3f} "
              f"RMSE={results[name]['rmse']:.3f} MAE={results[name]['mae']:.3f}")

    # Seasonal-average baseline for context (fit on train months, score hold-out).
    base = scores(y_te, seasonal_baseline(df_tr, df_te["Month"].to_numpy()))
    baseline = {"name": "Seasonal average", "r2": round(base["r2"], 4),
                "rmse": round(base["rmse"], 4), "mae": round(base["mae"], 4)}
    print(f"  {'Seasonal average':<18} (baseline)               | "
          f"hold-out R²={baseline['r2']:+.3f} RMSE={baseline['rmse']:.3f} "
          f"MAE={baseline['mae']:.3f}")

    # Pick the best model by CV RMSE (robust on small, noisy data).
    best_name = min(results, key=lambda k: results[k]["cvRmse"])
    # The interactive predictor needs a linear model (coefficients run in-browser).
    linear_name = min(linear_fits, key=lambda k: results[k]["cvRmse"])
    print(f"\n[best] {best_name} (lowest CV RMSE)")
    print(f"[predictor uses] {linear_name} (linear → runs client-side)\n")

    # Refit everything on ALL data for deployment / forecasting.
    scaler_full = StandardScaler().fit(X)
    X_sc = scaler_full.transform(X)
    fitted = {}
    for name, (est, needs_scaling, is_linear) in build_models().items():
        est.fit(X_sc if needs_scaling else X, y)
        fitted[name] = (est, needs_scaling)

    # Feature importance from the tree-based best model (or |std coef| if linear).
    importance = feature_importance(fitted, results, best_name, X_sc, X, y)

    return {
        "results": results,
        "baseline": baseline,
        "best_name": best_name,
        "linear_name": linear_name,
        "scaler_full": scaler_full,
        "fitted": fitted,
        "importance": importance,
    }


def feature_importance(fitted, results, best_name, X_sc, X, y):
    est, needs_scaling = fitted[best_name]
    Xuse = X_sc if needs_scaling else X
    if hasattr(est, "feature_importances_"):
        raw = est.feature_importances_
    else:
        raw = np.abs(getattr(est, "coef_", np.zeros(len(FEATURES))))
    # Direction: sign of the standardized linear coefficient (interpretable).
    lin = LinearRegression().fit(X_sc, y)
    signs = np.sign(lin.coef_)
    total = raw.sum() or 1.0
    out = []
    for i, key in enumerate(FEATURE_KEYS):
        out.append({
            "feature": key,
            "importance": round(float(raw[i] / total), 4),
            "direction": "up" if signs[i] >= 0 else "down",
        })
    out.sort(key=lambda d: d["importance"], reverse=True)
    return out


# ── Forecast the next 12 months ───────────────────────────────────────────────
def forecast(fitted, scaler_full, last_prev_month: int):
    prev = last_prev_month
    rows = []
    for y_, m_, oni, n34, wp, ws, hum, slp, mjo in FORECAST_SCENARIO:
        feat = np.array([[m_, oni, n34, wp, ws, hum, slp, mjo, prev]], dtype=float)
        feat_sc = scaler_full.transform(feat)
        preds = []
        for est, needs_scaling in fitted.values():
            p = est.predict(feat_sc if needs_scaling else feat)[0]
            preds.append(int(np.clip(round(p), 0, 12)))
        ens = int(np.clip(round(np.mean(preds)), 0, 12))
        rows.append({
            "year": y_, "month": m_, "typhoons": ens, "prevMonth": prev,
            "oni": oni, "nino34": n34, "wPacSST": wp, "windShear": ws,
            "humidity": hum, "slp": slp, "mjoPhase": mjo,
        })
        prev = ens
    return rows


# ── Export JSON for the frontend ──────────────────────────────────────────────
def record_from_row(row, predicted):
    oni = float(row["ONI"])
    month = int(row["Month"])
    return {
        "year": int(row["Year"]), "month": month, "monthName": MONTH_SHORT[month],
        "typhoons": int(row[TARGET]),
        "oni": round(oni, 3),
        "nino34": round(float(row["Nino3.4_SST_anomaly"]), 3),
        "wPacSST": round(float(row["Western_Pacific_SST"]), 3),
        "windShear": round(float(row["Vertical_Wind_Shear"]), 2),
        "humidity": round(float(row["Midlevel_Humidity"]), 2),
        "slp": round(float(row["SeaLevelPressure"]), 2),
        "mjoPhase": int(row["MJO_Phase"]),
        "prevMonth": int(row["Prev_month_typhoons"]),
        "ensoPhase": enso_phase(oni), "season": season(month),
        "predicted": predicted,
    }


def export(df, forecast_rows, train_out):
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)

    # data.json — history + model forecast
    records = [record_from_row(r, False) for _, r in df.iterrows()]
    for f in forecast_rows:
        records.append({
            "year": f["year"], "month": f["month"], "monthName": MONTH_SHORT[f["month"]],
            "typhoons": f["typhoons"],
            "oni": round(f["oni"], 3), "nino34": round(f["nino34"], 3),
            "wPacSST": round(f["wPacSST"], 3), "windShear": round(f["windShear"], 2),
            "humidity": round(f["humidity"], 2), "slp": round(f["slp"], 2),
            "mjoPhase": int(f["mjoPhase"]), "prevMonth": f["prevMonth"],
            "ensoPhase": enso_phase(f["oni"]), "season": season(f["month"]),
            "predicted": True,
        })
    with open(os.path.join(PUBLIC_DIR, "data.json"), "w") as fh:
        json.dump(records, fh)
    print(f"[export] public/data.json — {len(records)} records "
          f"({len(records) - len(forecast_rows)} history + {len(forecast_rows)} forecast)")

    # model.json — linear model for the browser predictor + honest metrics
    lin_name = train_out["linear_name"]
    lin_est = train_out["fitted"][lin_name][0]
    scaler = train_out["scaler_full"]
    data_through = f"{int(df.Year.iloc[-1])}-{int(df.Month.iloc[-1]):02d}"

    model_json = {
        "features": FEATURE_KEYS,
        "scaler": {
            "mean": [round(v, 6) for v in scaler.mean_.tolist()],
            "scale": [round(v, 6) for v in scaler.scale_.tolist()],
        },
        "coefficients": [round(v, 6) for v in lin_est.coef_.tolist()],
        "intercept": round(float(lin_est.intercept_), 6),
        "metrics": {
            name: {"cvR2": r["cvR2"], "cvRmse": r["cvRmse"],
                   "testR2": r["testR2"], "rmse": r["rmse"], "mae": r["mae"]}
            for name, r in train_out["results"].items()
        },
        "baseline": train_out["baseline"],
        "featureImportance": train_out["importance"],
        "bestModel": train_out["best_name"],
        "predictorModel": lin_name,
        "dataThrough": data_through,
        "holdoutMonths": HOLDOUT_MONTHS,
        "illustrative": True,
        "note": ("Trained on illustrative climate data for education/demo. "
                 "Metrics are cross-validated on a chronological hold-out. "
                 "Not an official PAGASA/NOAA forecast."),
    }
    with open(os.path.join(PUBLIC_DIR, "model.json"), "w") as fh:
        json.dump(model_json, fh, indent=2)
    print(f"[export] public/model.json — predictor uses {lin_name}, "
          f"best overall {train_out['best_name']}")

    # Local joblib artifacts (handy for further experiments; not used by the app)
    joblib.dump({n: e for n, (e, _) in train_out["fitted"].items()},
                os.path.join(MODEL_DIR, "all_models.joblib"))
    joblib.dump(train_out["fitted"][train_out["best_name"]][0],
                os.path.join(MODEL_DIR, "best_model.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.joblib"))
    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as fh:
        json.dump({"metrics": model_json["metrics"],
                   "baseline": model_json["baseline"],
                   "bestModel": model_json["bestModel"],
                   "dataThrough": data_through}, fh, indent=2)


def main():
    print("=" * 68)
    print("  BagyoSense-PH — honest training & export")
    print("=" * 68)
    df = load_data()
    train_out = train(df)
    last_actual_count = int(df[TARGET].iloc[-1])
    forecast_rows = forecast(train_out["fitted"], train_out["scaler_full"],
                             last_actual_count)
    print("[forecast] next 12 months (model ensemble under El Niño scenario):")
    print("           " + "  ".join(
        f"{MONTH_SHORT[f['month']]}{str(f['year'])[2:]}={f['typhoons']}"
        for f in forecast_rows))
    export(df, forecast_rows, train_out)
    print("\n[done] Refresh the app to see updated data & metrics.\n")


if __name__ == "__main__":
    main()
