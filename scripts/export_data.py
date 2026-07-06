"""
Export dataset and model coefficients to JSON for the Next.js frontend.
Run once before deploying:  python scripts/export_data.py
"""

import json
import os
import pandas as pd
import numpy as np
import joblib

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE_DIR, "dataset", "philippines_typhoon_monthly_2014_2024.csv")
MODEL_DIR  = os.path.join(BASE_DIR, "models")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

MONTH_SHORT = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}


def export_data():
    print("[DATA] Exporting dataset...")
    df = pd.read_csv(DATA_PATH)

    records = []
    for _, row in df.iterrows():
        oni = float(row["ONI"])
        month = int(row["Month"])
        records.append({
            "year": int(row["Year"]),
            "month": month,
            "monthName": MONTH_SHORT[month],
            "typhoons": int(row["Number_of_Typhoons"]),
            "oni": round(oni, 3),
            "nino34": round(float(row["Nino3.4_SST_anomaly"]), 3),
            "wPacSST": round(float(row["Western_Pacific_SST"]), 3),
            "windShear": round(float(row["Vertical_Wind_Shear"]), 2),
            "humidity": round(float(row["Midlevel_Humidity"]), 2),
            "slp": round(float(row["SeaLevelPressure"]), 2),
            "mjoPhase": int(row["MJO_Phase"]),
            "prevMonth": int(row["Prev_month_typhoons"]),
            "ensoPhase": (
                "El Nino" if oni >= 0.5
                else ("La Nina" if oni <= -0.5 else "Neutral")
            ),
            "season": "Peak" if 6 <= month <= 11 else "Off-Season",
        })

    os.makedirs(PUBLIC_DIR, exist_ok=True)
    with open(os.path.join(PUBLIC_DIR, "data.json"), "w") as f:
        json.dump(records, f)

    print(f"    -> {len(records)} records saved to public/data.json")


def export_model():
    print("[MODEL] Exporting model coefficients...")

    models_dict = joblib.load(os.path.join(MODEL_DIR, "all_models.joblib"))
    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.joblib"))

    with open(os.path.join(MODEL_DIR, "metrics.json")) as f:
        raw_metrics = json.load(f)

    lr_model = models_dict["Linear Regression"]["model"]

    metrics = {}
    for name, m in raw_metrics.items():
        if name.startswith("_"):
            continue
        metrics[name] = {
            "cvR2": m.get("cv_r2"),
            "testR2": m.get("test_r2"),
            "rmse": m.get("rmse"),
            "mae": m.get("mae"),
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
        "bestModel": raw_metrics.get("_best_model", "XGBoost"),
    }

    with open(os.path.join(PUBLIC_DIR, "model.json"), "w") as f:
        json.dump(model_data, f, indent=2)

    print(f"    -> Model data saved to public/model.json")
    print(f"    -> Best model: {model_data['bestModel']}")


if __name__ == "__main__":
    export_data()
    export_model()
    print("\n[DONE] Export complete.")
