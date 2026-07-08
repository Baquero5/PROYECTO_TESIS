"""
Script 08: Crear ensemble XGBoost + LightGBM
Entrada: models/xgboost_model.pkl, models/lightgbm_model.pkl
Salida: models/ensemble.pkl, models/ensemble_weights.pkl
"""
import pandas as pd
import numpy as np
import joblib
import json
import yaml
import time
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
METRICS_DIR = BASE_DIR / "metrics"

with open(BASE_DIR / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

FEATURE_COLS = config["features"]
ENSEMBLE_WEIGHTS = config["ensemble"]


def load_data():
    print("[1/4] Cargando dataset...")
    df = pd.read_csv(PROC_DIR / "dataset_entrenamiento.csv")
    X = df[FEATURE_COLS].fillna(0)
    y = df["y"].fillna(0)
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"  Test: {X_test.shape[0]:,} muestras")
    return X_test, y_test


def load_models():
    print("\n[2/4] Cargando modelos...")
    xgb_model = joblib.load(MODELS_DIR / "xgboost_model.pkl")
    lgb_model = joblib.load(MODELS_DIR / "lightgbm_model.pkl")
    print("  [OK] XGBoost cargado")
    print("  [OK] LightGBM cargado")
    return xgb_model, lgb_model


def create_ensemble(xgb_model, lgb_model, X_test, y_test):
    print("\n[3/4] Creando ensemble ponderado...")

    w_xgb = ENSEMBLE_WEIGHTS["xgboost_weight"]
    w_lgb = ENSEMBLE_WEIGHTS["lightgbm_weight"]

    xgb_pred = np.maximum(xgb_model.predict(X_test), 0)
    lgb_pred = np.maximum(lgb_model.predict(X_test), 0)

    ensemble_pred = w_xgb * xgb_pred + w_lgb * lgb_pred
    ensemble_pred = np.maximum(ensemble_pred, 0)

    mae = float(mean_absolute_error(y_test, ensemble_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, ensemble_pred)))
    r2 = float(r2_score(y_test, ensemble_pred))
    mape = float(np.mean(np.abs((y_test - ensemble_pred) / np.maximum(y_test, 1))) * 100)

    print(f"  Pesos: XGBoost={w_xgb}, LightGBM={w_lgb}")
    print(f"  Ensemble Metrics:")
    print(f"    MAE:  {mae:.4f}")
    print(f"    RMSE: {rmse:.4f}")
    print(f"    R2:   {r2:.4f}")
    print(f"    MAPE: {mape:.4f}%")

    metrics = {
        "modelo": "Ensemble (XGBoost + LightGBM)",
        "version": "1.0",
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2": round(r2, 4),
        "mape": round(mape, 4),
        "pesos": {"xgboost": w_xgb, "lightgbm": w_lgb},
        "features_used": FEATURE_COLS,
    }

    return metrics


def save_ensemble(metrics):
    print("\n[4/4] Guardando ensemble...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    ensemble_data = {
        "xgb_model_file": "xgboost_model.pkl",
        "lgb_model_file": "lightgbm_model.pkl",
        "xgb_weight": ENSEMBLE_WEIGHTS["xgboost_weight"],
        "lgb_weight": ENSEMBLE_WEIGHTS["lightgbm_weight"],
    }
    joblib.dump(ensemble_data, MODELS_DIR / "ensemble.pkl")
    print("  [OK] ensemble.pkl guardado")

    joblib.dump(ENSEMBLE_WEIGHTS, MODELS_DIR / "ensemble_weights.pkl")
    print("  [OK] ensemble_weights.pkl guardado")

    with open(METRICS_DIR / "ensemble_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print("  [OK] ensemble_metrics.json guardado")


def main():
    print("=" * 60)
    print("CREAR ENSEMBLE XGBOOST + LIGHTGBM")
    print("=" * 60)

    X_test, y_test = load_data()
    xgb_model, lgb_model = load_models()
    metrics = create_ensemble(xgb_model, lgb_model, X_test, y_test)
    save_ensemble(metrics)

    print("\n[OK] Ensemble creado exitosamente!")


if __name__ == "__main__":
    main()
