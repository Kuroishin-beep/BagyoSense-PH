"""
BagyoSense-PH — Model Training Pipeline
=========================================
Standalone script that downloads XGBoost (pretrained gradient boosting framework),
finetunes it on the Philippines typhoon dataset using 5-fold cross-validation
with hyperparameter tuning, and saves all models to disk.

Usage:
    python train_model.py

Models are saved to  models/  and loaded by the Streamlit app on startup.
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score, GridSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from xgboost import XGBRegressor

warnings.filterwarnings("ignore", category=UserWarning)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "dataset", "philippines_typhoon_monthly_2014_2024.csv")
MODEL_DIR  = os.path.join(BASE_DIR, "models")

FEATURES = [
    "Month", "ONI", "Nino3.4_SST_anomaly", "Western_Pacific_SST",
    "Vertical_Wind_Shear", "Midlevel_Humidity", "SeaLevelPressure",
    "MJO_Phase", "Prev_month_typhoons",
]
TARGET = "Number_of_Typhoons"


def load_data() -> pd.DataFrame:
    """Load and return the typhoon dataset."""
    print(f"[DATA] Loading data from {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"    -> {len(df)} rows, {len(df.columns)} columns\n")
    return df


def build_models() -> dict:
    """Return a dict of model name → (model_instance, param_grid)."""
    return {
        "XGBoost": (
            XGBRegressor(
                objective="reg:squarederror",
                random_state=42,
                verbosity=0,
                n_jobs=-1,
            ),
            {
                "n_estimators":    [100, 200, 300],
                "max_depth":       [3, 4, 6],
                "learning_rate":   [0.05, 0.1, 0.2],
                "subsample":       [0.8, 1.0],
                "colsample_bytree": [0.8, 1.0],
            },
        ),
        "Random Forest": (
            RandomForestRegressor(random_state=42, n_jobs=-1),
            {
                "n_estimators": [100, 200, 300],
                "max_depth":    [4, 6, 8, None],
                "min_samples_split": [2, 5],
            },
        ),
        "Gradient Boosting": (
            GradientBoostingRegressor(random_state=42),
            {
                "n_estimators":  [100, 200, 300],
                "max_depth":     [3, 4, 5],
                "learning_rate": [0.05, 0.1, 0.2],
            },
        ),
        "Linear Regression": (
            LinearRegression(),
            {},  # no hyperparams to tune
        ),
    }


def train_and_evaluate(df: pd.DataFrame) -> dict:
    """
    Train all models with 5-fold cross-validation + grid search,
    evaluate on a held-out test set, and return results dict.
    """
    X = df[FEATURES].copy()
    y = df[TARGET].copy()

    # Hold out 20% for final evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Scaler for Linear Regression
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    models_spec = build_models()
    results = {}
    best_score = -np.inf
    best_name  = None

    print("=" * 65)
    print("  BagyoSense-PH — Model Training Pipeline")
    print("=" * 65)
    print(f"  Training set:  {len(X_train)} samples")
    print(f"  Test set:      {len(X_test)} samples")
    print(f"  Features:      {len(FEATURES)}")
    print(f"  CV folds:      5")
    print("=" * 65)
    print()

    for name, (model, param_grid) in models_spec.items():
        print(f"[TRAIN] Training {name}...")

        use_scaled = name == "Linear Regression"
        X_tr = X_train_sc if use_scaled else X_train
        X_te = X_test_sc  if use_scaled else X_test

        # Hyperparameter tuning with GridSearchCV (5-fold CV)
        if param_grid:
            grid = GridSearchCV(
                model,
                param_grid,
                cv=5,
                scoring="r2",
                n_jobs=-1,
                refit=True,
            )
            grid.fit(X_tr, y_train)
            fitted_model = grid.best_estimator_
            cv_score = grid.best_score_
            best_params = grid.best_params_
            print(f"    Best params: {best_params}")
        else:
            fitted_model = model
            fitted_model.fit(X_tr, y_train)
            cv_scores = cross_val_score(fitted_model, X_tr, y_train, cv=5, scoring="r2")
            cv_score = cv_scores.mean()
            best_params = {}

        # Predict on held-out test set
        raw_preds = fitted_model.predict(X_te)
        preds = np.clip(np.round(raw_preds), 0, None)

        r2   = r2_score(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        mae  = mean_absolute_error(y_test, preds)

        results[name] = {
            "model":       fitted_model,
            "cv_r2":       round(float(cv_score), 4),
            "test_r2":     round(float(r2), 4),
            "rmse":        round(float(rmse), 4),
            "mae":         round(float(mae), 4),
            "best_params": best_params,
            "preds":       preds.tolist(),
            "y_test":      y_test.values.tolist(),
            "uses_scaler": use_scaled,
        }

        print(f"    CV R²:   {cv_score:.4f}")
        print(f"    Test R²: {r2:.4f}  |  RMSE: {rmse:.4f}  |  MAE: {mae:.4f}")
        print()

        if cv_score > best_score:
            best_score = cv_score
            best_name  = name

    print("=" * 65)
    print(f"  >> Best model: {best_name}  (CV R2 = {best_score:.4f})")
    print("=" * 65)

    return results, scaler, best_name


def save_models(results: dict, scaler: StandardScaler, best_name: str):
    """Persist models, scaler, and metrics to the models/ directory."""
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Save all models
    models_dict = {}
    for name, res in results.items():
        models_dict[name] = {
            "model":       res["model"],
            "uses_scaler": res["uses_scaler"],
        }
    joblib.dump(models_dict, os.path.join(MODEL_DIR, "all_models.joblib"))

    # Save the best model separately for quick loading
    joblib.dump(results[best_name]["model"], os.path.join(MODEL_DIR, "best_model.joblib"))

    # Save scaler
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.joblib"))

    # Save metrics as JSON (for display in the Streamlit app)
    metrics = {}
    for name, res in results.items():
        metrics[name] = {
            "cv_r2":       res["cv_r2"],
            "test_r2":     res["test_r2"],
            "rmse":        res["rmse"],
            "mae":         res["mae"],
            "best_params": res["best_params"],
            "uses_scaler": res["uses_scaler"],
        }
    metrics["_best_model"] = best_name
    metrics["_features"]   = FEATURES
    metrics["_target"]     = TARGET

    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[SAVE] Models saved to {MODEL_DIR}/")
    print(f"    - all_models.joblib")
    print(f"    - best_model.joblib")
    print(f"    - scaler.joblib")
    print(f"    - metrics.json")


def print_comparison_table(results: dict, best_name: str):
    """Print a formatted comparison table of all models."""
    print("\n" + "=" * 65)
    print("  MODEL COMPARISON TABLE")
    print("=" * 65)
    print(f"  {'Model':<22} {'CV R²':>8} {'Test R²':>8} {'RMSE':>8} {'MAE':>8}")
    print("  " + "-" * 58)
    for name, res in results.items():
        marker = " << BEST" if name == best_name else ""
        print(
            f"  {name:<22} {res['cv_r2']:>8.4f} {res['test_r2']:>8.4f} "
            f"{res['rmse']:>8.4f} {res['mae']:>8.4f}{marker}"
        )
    print("=" * 65)


if __name__ == "__main__":
    df = load_data()
    results, scaler, best_name = train_and_evaluate(df)
    print_comparison_table(results, best_name)
    save_models(results, scaler, best_name)
    print("\n[DONE] Training complete! Run  streamlit run app.py  to use the models.\n")
