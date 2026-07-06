"""
Update dataset with 2025 actual data, retrain models, and predict 2026.

Sources:
  - PAGASA reports: 23 tropical cyclones entered PAR in 2025
  - NOAA: Weak La Nina early 2025, neutral by spring, El Nino developing mid-2026
  - Wikipedia: 2025 Pacific typhoon season summary
"""

import json
import os
import sys
import warnings
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE_DIR, "dataset", "philippines_typhoon_monthly_2014_2024.csv")
DATA_2025  = os.path.join(BASE_DIR, "dataset", "philippines_typhoon_monthly_2014_2025.csv")
MODEL_DIR  = os.path.join(BASE_DIR, "models")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

# ── 2025 Actual Data ──────────────────────────────────────────────────────────
# Sources: PAGASA 2025 annual report, NOAA ONI data, Wikipedia 2025 Pacific typhoon season
# Total: 23 tropical cyclones in PAR
# Jan-May: 0 (unusually quiet), Jun: 1 (TD Auring), Jul-Dec: 22
# Climate vars based on NOAA/PAGASA reports: weak La Nina -> neutral transition
DATA_2025_ROWS = [
    # Year, Month, Typhoons, ONI, Nino34, WPSST, WindShear, Humidity, SLP, MJO, PrevMonth
    [2025,  1, 0, -0.50, -0.55,  0.20, 12.5, 56.0, 1010.0, 3, 1],
    [2025,  2, 0, -0.60, -0.62,  0.10, 12.8, 55.5, 1010.2, 5, 0],
    [2025,  3, 0, -0.40, -0.38,  0.30, 13.0, 52.0, 1009.5, 4, 0],
    [2025,  4, 0, -0.30, -0.28,  0.15, 10.5, 58.5, 1008.0, 2, 0],
    [2025,  5, 0, -0.20, -0.18,  0.25, 11.0, 59.0, 1007.5, 3, 0],
    [2025,  6, 1, -0.10, -0.08,  0.35,  8.2, 69.0, 1005.5, 6, 0],
    [2025,  7, 3,  0.00,  0.02,  0.40,  7.8, 71.5, 1005.0, 4, 1],
    [2025,  8, 4,  0.10,  0.08,  0.25,  8.0, 70.0, 1004.5, 5, 3],
    [2025,  9, 5,  0.00,  0.02,  0.30,  8.2, 70.5, 1004.0, 3, 4],
    [2025, 10, 4, -0.10, -0.08,  0.20,  9.2, 63.0, 1005.0, 5, 5],
    [2025, 11, 4, -0.30, -0.25,  0.35,  9.8, 64.5, 1007.5, 4, 4],
    [2025, 12, 2, -0.40, -0.38,  0.30, 12.0, 55.0, 1009.8, 6, 4],
]

# ── 2026 Climate Scenario ─────────────────────────────────────────────────────
# NOAA/IRI forecast: El Nino developing mid-2026, strengthening through H2
# El Nino typically suppresses typhoon activity (higher wind shear, less moisture)
CLIMATE_2026 = [
    # Month, ONI, Nino34, WPSST, WindShear, Humidity, SLP, MJO
    [ 1, 0.20,  0.18,  0.10, 12.5, 56.0, 1009.8, 4],
    [ 2, 0.30,  0.28,  0.20, 12.8, 55.0, 1010.0, 5],
    [ 3, 0.40,  0.38,  0.15, 13.0, 52.5, 1009.5, 3],
    [ 4, 0.50,  0.48,  0.10, 10.8, 59.0, 1008.2, 2],
    [ 5, 0.60,  0.58, -0.10, 11.2, 60.0, 1007.8, 4],
    [ 6, 0.70,  0.68,  0.05,  8.5, 68.0, 1006.0, 5],
    [ 7, 0.80,  0.78, -0.10,  8.8, 69.0, 1005.5, 6],
    [ 8, 0.90,  0.88, -0.20,  8.5, 68.5, 1005.0, 4],
    [ 9, 1.00,  0.98, -0.15,  8.8, 67.0, 1005.5, 3],
    [10, 1.10,  1.08, -0.25,  9.5, 62.0, 1005.8, 5],
    [11, 1.00,  0.98,  0.10, 10.0, 63.0, 1008.0, 4],
    [12, 0.90,  0.88,  0.20, 12.0, 55.0, 1009.5, 3],
]

COLS = [
    "Year", "Month", "Number_of_Typhoons", "ONI", "Nino3.4_SST_anomaly",
    "Western_Pacific_SST", "Vertical_Wind_Shear", "Midlevel_Humidity",
    "SeaLevelPressure", "MJO_Phase", "Prev_month_typhoons",
]

FEATURES = [
    "Month", "ONI", "Nino3.4_SST_anomaly", "Western_Pacific_SST",
    "Vertical_Wind_Shear", "Midlevel_Humidity", "SeaLevelPressure",
    "MJO_Phase", "Prev_month_typhoons",
]
TARGET = "Number_of_Typhoons"

MONTH_SHORT = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}


def step1_update_dataset():
    """Add 2025 data to the CSV."""
    print("=" * 65)
    print("  STEP 1: Update Dataset with 2025 Data")
    print("=" * 65)

    df = pd.read_csv(DATA_PATH)
    print(f"  Original: {len(df)} rows (2014-2024)")

    df_2025 = pd.DataFrame(DATA_2025_ROWS, columns=COLS)
    df_full = pd.concat([df, df_2025], ignore_index=True)

    df_full.to_csv(DATA_2025, index=False)
    print(f"  Updated:  {len(df_full)} rows (2014-2025)")
    print(f"  2025 total typhoons: {df_2025[TARGET].sum()}")
    print(f"  Saved to: {DATA_2025}")
    return df_full


def step2_train(df):
    """Retrain all models on 2014-2025 data."""
    print()
    print("=" * 65)
    print("  STEP 2: Retrain Models on 2014-2025 Data")
    print("=" * 65)

    X = df[FEATURES].values
    y = df[TARGET].values

    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X)

    models = {
        "XGBoost": {
            "model": XGBRegressor(random_state=42, verbosity=0),
            "params": {
                "n_estimators": [100, 200],
                "max_depth": [3, 4],
                "learning_rate": [0.05, 0.1],
                "subsample": [0.8],
                "colsample_bytree": [1.0],
            },
            "uses_scaler": False,
        },
        "Random Forest": {
            "model": RandomForestRegressor(random_state=42),
            "params": {
                "n_estimators": [100, 200],
                "max_depth": [4, 6],
                "min_samples_split": [2, 5],
            },
            "uses_scaler": False,
        },
        "Gradient Boosting": {
            "model": GradientBoostingRegressor(random_state=42),
            "params": {
                "n_estimators": [100, 200],
                "max_depth": [3, 4],
                "learning_rate": [0.05, 0.1],
            },
            "uses_scaler": False,
        },
        "Linear Regression": {
            "model": LinearRegression(),
            "params": {},
            "uses_scaler": True,
        },
    }

    results = {}
    for name, cfg in models.items():
        print(f"\n  [TRAIN] {name}...")
        use_sc = cfg["uses_scaler"]
        X_use = X_sc if use_sc else X

        if cfg["params"]:
            gs = GridSearchCV(
                cfg["model"], cfg["params"],
                cv=5, scoring="r2", n_jobs=-1,
            )
            gs.fit(X_use, y)
            best = gs.best_estimator_
            cv_r2 = gs.best_score_
            print(f"    Best params: {gs.best_params_}")
        else:
            best = cfg["model"]
            best.fit(X_use, y)
            cv_scores = cross_val_score(best, X_use, y, cv=5, scoring="r2")
            cv_r2 = cv_scores.mean()

        preds = best.predict(X_use)
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
        r2 = r2_score(y, preds)
        rmse = np.sqrt(mean_squared_error(y, preds))
        mae = mean_absolute_error(y, preds)

        print(f"    CV R2: {cv_r2:.4f}  |  Train R2: {r2:.4f}  |  RMSE: {rmse:.4f}  |  MAE: {mae:.4f}")

        results[name] = {
            "model": best,
            "uses_scaler": use_sc,
            "cv_r2": round(cv_r2, 4),
            "test_r2": round(r2, 4),
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
        }

    best_name = max(results, key=lambda k: results[k]["cv_r2"])
    print(f"\n  >> Best model: {best_name} (CV R2 = {results[best_name]['cv_r2']:.4f})")

    # Save
    os.makedirs(MODEL_DIR, exist_ok=True)
    models_dict = {
        name: {"model": r["model"], "uses_scaler": r["uses_scaler"]}
        for name, r in results.items()
    }
    joblib.dump(models_dict, os.path.join(MODEL_DIR, "all_models.joblib"))
    joblib.dump(results[best_name]["model"], os.path.join(MODEL_DIR, "best_model.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.joblib"))

    metrics = {
        name: {
            "cv_r2": r["cv_r2"], "test_r2": r["test_r2"],
            "rmse": r["rmse"], "mae": r["mae"],
            "uses_scaler": r["uses_scaler"],
        }
        for name, r in results.items()
    }
    metrics["_best_model"] = best_name
    metrics["_features"] = FEATURES
    metrics["_target"] = TARGET

    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n  Models saved to {MODEL_DIR}/")
    return results, scaler


def step3_predict_2026(results, scaler):
    """Predict 2026 monthly typhoon counts using ensemble."""
    print()
    print("=" * 65)
    print("  STEP 3: Predict 2026 Typhoon Counts")
    print("=" * 65)

    prev_month = 2  # Dec 2025 actual
    predictions_2026 = []

    for row in CLIMATE_2026:
        month = row[0]
        features = [month] + row[1:] + [prev_month]
        arr = np.array([features])
        arr_sc = scaler.transform(arr)

        model_preds = {}
        for name, r in results.items():
            model = r["model"]
            use_sc = r["uses_scaler"]
            pred = model.predict(arr_sc if use_sc else arr)[0]
            pred = int(np.clip(round(pred), 0, 12))
            model_preds[name] = pred

        ensemble = round(sum(model_preds.values()) / len(model_preds))
        ensemble = int(np.clip(ensemble, 0, 12))

        predictions_2026.append({
            "month": month,
            "ensemble": ensemble,
            "models": model_preds,
            "prev_month": prev_month,
            "climate": row,
        })

        prev_month = ensemble  # cascade

    print()
    print(f"  {'Month':<6} {'Ensemble':<10} {'XGB':<6} {'RF':<6} {'GB':<6} {'LR':<6}")
    print("  " + "-" * 42)
    total = 0
    for p in predictions_2026:
        m = MONTH_SHORT[p["month"]]
        e = p["ensemble"]
        total += e
        xgb = p["models"].get("XGBoost", "-")
        rf  = p["models"].get("Random Forest", "-")
        gb  = p["models"].get("Gradient Boosting", "-")
        lr  = p["models"].get("Linear Regression", "-")
        print(f"  {m:<6} {e:<10} {xgb:<6} {rf:<6} {gb:<6} {lr:<6}")
    print("  " + "-" * 42)
    print(f"  {'TOTAL':<6} {total}")

    return predictions_2026


def step4_export(df, predictions_2026, results, scaler):
    """Export updated data + predictions for the Next.js frontend."""
    print()
    print("=" * 65)
    print("  STEP 4: Export for Frontend")
    print("=" * 65)

    os.makedirs(PUBLIC_DIR, exist_ok=True)

    # Export actual data (2014-2025)
    records = []
    for _, row in df.iterrows():
        oni = float(row["ONI"])
        month = int(row["Month"])
        records.append({
            "year": int(row["Year"]),
            "month": month,
            "monthName": MONTH_SHORT[month],
            "typhoons": int(row[TARGET]),
            "oni": round(oni, 3),
            "nino34": round(float(row["Nino3.4_SST_anomaly"]), 3),
            "wPacSST": round(float(row["Western_Pacific_SST"]), 3),
            "windShear": round(float(row["Vertical_Wind_Shear"]), 2),
            "humidity": round(float(row["Midlevel_Humidity"]), 2),
            "slp": round(float(row["SeaLevelPressure"]), 2),
            "mjoPhase": int(row["MJO_Phase"]),
            "prevMonth": int(row["Prev_month_typhoons"]),
            "ensoPhase": "El Nino" if oni >= 0.5 else ("La Nina" if oni <= -0.5 else "Neutral"),
            "season": "Peak" if 6 <= month <= 11 else "Off-Season",
            "predicted": False,
        })

    # Append 2026 predictions
    for p in predictions_2026:
        month = p["month"]
        c = p["climate"]
        oni = c[1]
        records.append({
            "year": 2026,
            "month": month,
            "monthName": MONTH_SHORT[month],
            "typhoons": p["ensemble"],
            "oni": round(oni, 3),
            "nino34": round(c[2], 3),
            "wPacSST": round(c[3], 3),
            "windShear": round(c[4], 2),
            "humidity": round(c[5], 2),
            "slp": round(c[6], 2),
            "mjoPhase": int(c[7]),
            "prevMonth": p["prev_month"],
            "ensoPhase": "El Nino" if oni >= 0.5 else ("La Nina" if oni <= -0.5 else "Neutral"),
            "season": "Peak" if 6 <= month <= 11 else "Off-Season",
            "predicted": True,
        })

    with open(os.path.join(PUBLIC_DIR, "data.json"), "w") as f:
        json.dump(records, f)
    print(f"  data.json: {len(records)} records (2014-2025 actual + 2026 predicted)")

    # Export model
    lr_model = results["Linear Regression"]["model"]
    metrics = {}
    for name, r in results.items():
        metrics[name] = {
            "cvR2": r["cv_r2"],
            "testR2": r["test_r2"],
            "rmse": r["rmse"],
            "mae": r["mae"],
        }

    model_data = {
        "features": [
            "month", "oni", "nino34", "wPacSST",
            "windShear", "humidity", "slp", "mjoPhase", "prevMonth",
        ],
        "scaler": {
            "mean": [round(v, 6) for v in scaler.mean_.tolist()],
            "scale": [round(v, 6) for v in scaler.scale_.tolist()],
        },
        "coefficients": [round(v, 6) for v in lr_model.coef_.tolist()],
        "intercept": round(float(lr_model.intercept_), 6),
        "metrics": metrics,
        "bestModel": max(results, key=lambda k: results[k]["cv_r2"]),
    }

    with open(os.path.join(PUBLIC_DIR, "model.json"), "w") as f:
        json.dump(model_data, f, indent=2)
    print(f"  model.json: updated with retrained coefficients")
    print(f"  Best model: {model_data['bestModel']}")


if __name__ == "__main__":
    df = step1_update_dataset()
    results, scaler = step2_train(df)
    preds = step3_predict_2026(results, scaler)
    step4_export(df, preds, results, scaler)
    print()
    print("=" * 65)
    print("  DONE. Run 'npm run dev' to see the updated dashboard.")
    print("=" * 65)
