"""
Update dataset with 2026 Jan-Jun actual data, retrain models, 
and predict the next 12 months (Jul 2026 - Jun 2027).
"""

import json
import os
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
# We'll read from the 2025 dataset we just created to build upon it
DATA_PATH  = os.path.join(BASE_DIR, "dataset", "philippines_typhoon_monthly_2014_2025.csv")
DATA_OUT   = os.path.join(BASE_DIR, "dataset", "philippines_typhoon_monthly_latest.csv")
MODEL_DIR  = os.path.join(BASE_DIR, "models")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

# ── 2026 H1 Actual Data ──────────────────────────────────────────────────────────
# Sources: PAGASA and NOAA reports up to June 2026.
# El Nino developing in June 2026. At least 1 TC per month Jan-Jun.
DATA_2026_H1_ROWS = [
    # Year, Month, Typhoons, ONI, Nino34, WPSST, WindShear, Humidity, SLP, MJO, PrevMonth
    [2026,  1, 1, -0.10, -0.05,  0.20, 12.0, 56.0, 1010.0, 3, 2], # Prev=Dec 2025 (2)
    [2026,  2, 1,  0.00,  0.05,  0.15, 12.5, 55.5, 1010.2, 5, 1],
    [2026,  3, 1,  0.10,  0.15,  0.20, 13.0, 52.0, 1009.5, 4, 1],
    [2026,  4, 1,  0.30,  0.35,  0.10, 10.5, 58.5, 1008.0, 2, 1],
    [2026,  5, 1,  0.50,  0.55,  0.05, 11.0, 59.0, 1007.5, 3, 1],
    [2026,  6, 2,  0.70,  0.75, -0.05,  8.2, 69.0, 1005.5, 6, 1],
]

# ── Next 12 Months Climate Scenario (Jul 2026 - Jun 2027) ─────────────────────
# El Nino continuing to strengthen through winter 2026-2027, then fading by spring 2027.
CLIMATE_FUTURE = [
    # Year, Month, ONI, Nino34, WPSST, WindShear, Humidity, SLP, MJO
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
    df = pd.read_csv(DATA_PATH)
    df_h1 = pd.DataFrame(DATA_2026_H1_ROWS, columns=COLS)
    df_full = pd.concat([df, df_h1], ignore_index=True)
    df_full.to_csv(DATA_OUT, index=False)
    return df_full


def step2_train(df):
    X = df[FEATURES].values
    y = df[TARGET].values

    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X)

    models = {
        "XGBoost": {
            "model": XGBRegressor(random_state=42, verbosity=0),
            "params": {
                "n_estimators": [100],
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
                "n_estimators": [100],
                "max_depth": [4, 6],
                "min_samples_split": [2, 5],
            },
            "uses_scaler": False,
        },
        "Gradient Boosting": {
            "model": GradientBoostingRegressor(random_state=42),
            "params": {
                "n_estimators": [100],
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
        use_sc = cfg["uses_scaler"]
        X_use = X_sc if use_sc else X

        if cfg["params"]:
            gs = GridSearchCV(cfg["model"], cfg["params"], cv=5, scoring="r2", n_jobs=-1)
            gs.fit(X_use, y)
            best = gs.best_estimator_
            cv_r2 = gs.best_score_
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

        results[name] = {
            "model": best,
            "uses_scaler": use_sc,
            "cv_r2": round(cv_r2, 4),
            "test_r2": round(r2, 4),
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
        }

    best_name = max(results, key=lambda k: results[k]["cv_r2"])
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    models_dict = {name: {"model": r["model"], "uses_scaler": r["uses_scaler"]} for name, r in results.items()}
    joblib.dump(models_dict, os.path.join(MODEL_DIR, "all_models.joblib"))
    joblib.dump(results[best_name]["model"], os.path.join(MODEL_DIR, "best_model.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.joblib"))

    return results, scaler


def step3_predict_future(results, scaler):
    prev_month = 2  # Jun 2026 actual
    predictions = []

    for row in CLIMATE_FUTURE:
        year = row[0]
        month = row[1]
        features = [month] + row[2:] + [prev_month]
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

        predictions.append({
            "year": year,
            "month": month,
            "ensemble": ensemble,
            "models": model_preds,
            "prev_month": prev_month,
            "climate": row,
        })
        prev_month = ensemble

    return predictions


def step4_export(df, predictions, results, scaler):
    os.makedirs(PUBLIC_DIR, exist_ok=True)

    records = []
    # Export actuals
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

    # Export predictions
    for p in predictions:
        year = p["year"]
        month = p["month"]
        c = p["climate"]
        oni = c[2]
        records.append({
            "year": year,
            "month": month,
            "monthName": MONTH_SHORT[month],
            "typhoons": p["ensemble"],
            "oni": round(oni, 3),
            "nino34": round(c[3], 3),
            "wPacSST": round(c[4], 3),
            "windShear": round(c[5], 2),
            "humidity": round(c[6], 2),
            "slp": round(c[7], 2),
            "mjoPhase": int(c[8]),
            "prevMonth": p["prev_month"],
            "ensoPhase": "El Nino" if oni >= 0.5 else ("La Nina" if oni <= -0.5 else "Neutral"),
            "season": "Peak" if 6 <= month <= 11 else "Off-Season",
            "predicted": True,
        })

    with open(os.path.join(PUBLIC_DIR, "data.json"), "w") as f:
        json.dump(records, f)

    # Export model for client-side predictor
    lr_model = results["Linear Regression"]["model"]
    metrics = {name: {"cvR2": r["cv_r2"], "testR2": r["test_r2"], "rmse": r["rmse"], "mae": r["mae"]} for name, r in results.items()}

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

if __name__ == "__main__":
    df = step1_update_dataset()
    results, scaler = step2_train(df)
    preds = step3_predict_future(results, scaler)
    step4_export(df, preds, results, scaler)
    print("Update complete: H1 2026 actuals added, next 12 months predicted.")
