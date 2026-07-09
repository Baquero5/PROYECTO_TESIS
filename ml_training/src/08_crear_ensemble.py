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

DIRECTORIO_BASE = Path(__file__).resolve().parent.parent
DIRECTORIO_PROCESADO = DIRECTORIO_BASE / "data" / "processed"
DIRECTORIO_MODELOS = DIRECTORIO_BASE / "models"
DIRECTORIO_METRICAS = DIRECTORIO_BASE / "metrics"

with open(DIRECTORIO_BASE / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

COLUMNAS_FEATURES = config["features"]
PESOS_ENSEMBLE = config["ensemble"]


def cargar_datos():
    print("[1/4] Cargando dataset...")
    df = pd.read_csv(DIRECTORIO_PROCESADO / "dataset_entrenamiento.csv")
    X = df[COLUMNAS_FEATURES].fillna(0)
    y = df["y"].fillna(0)
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"  Test: {X_test.shape[0]:,} muestras")
    return X_test, y_test


def cargar_modelos():
    print("\n[2/4] Cargando modelos...")
    modelo_xgb = joblib.load(DIRECTORIO_MODELOS / "xgboost_model.pkl")
    modelo_lgb = joblib.load(DIRECTORIO_MODELOS / "lightgbm_model.pkl")
    print("  [OK] XGBoost cargado")
    print("  [OK] LightGBM cargado")
    return modelo_xgb, modelo_lgb


def crear_ensemble(modelo_xgb, modelo_lgb, X_test, y_test):
    print("\n[3/4] Creando ensemble ponderado...")

    peso_xgb = PESOS_ENSEMBLE["xgboost_weight"]
    peso_lgb = PESOS_ENSEMBLE["lightgbm_weight"]

    pred_xgb = np.maximum(modelo_xgb.predict(X_test), 0)
    pred_lgb = np.maximum(modelo_lgb.predict(X_test), 0)

    pred_ensemble = peso_xgb * pred_xgb + peso_lgb * pred_lgb
    pred_ensemble = np.maximum(pred_ensemble, 0)

    mae = float(mean_absolute_error(y_test, pred_ensemble))
    rmse = float(np.sqrt(mean_squared_error(y_test, pred_ensemble)))
    r2 = float(r2_score(y_test, pred_ensemble))
    mape = float(np.mean(np.abs((y_test - pred_ensemble) / np.maximum(y_test, 1))) * 100)

    print(f"  Pesos: XGBoost={peso_xgb}, LightGBM={peso_lgb}")
    print(f"  Ensemble Metrics:")
    print(f"    MAE:  {mae:.4f}")
    print(f"    RMSE: {rmse:.4f}")
    print(f"    R2:   {r2:.4f}")
    print(f"    MAPE: {mape:.4f}%")

    metricas = {
        "modelo": "Ensemble (XGBoost + LightGBM)",
        "version": "1.0",
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2": round(r2, 4),
        "mape": round(mape, 4),
        "pesos": {"xgboost": peso_xgb, "lightgbm": peso_lgb},
        "features_used": COLUMNAS_FEATURES,
    }

    return metricas


def guardar_ensemble(metricas):
    print("\n[4/4] Guardando ensemble...")
    DIRECTORIO_MODELOS.mkdir(parents=True, exist_ok=True)
    DIRECTORIO_METRICAS.mkdir(parents=True, exist_ok=True)

    datos_ensemble = {
        "xgb_model_file": "xgboost_model.pkl",
        "lgb_model_file": "lightgbm_model.pkl",
        "xgb_weight": PESOS_ENSEMBLE["xgboost_weight"],
        "lgb_weight": PESOS_ENSEMBLE["lightgbm_weight"],
    }
    joblib.dump(datos_ensemble, DIRECTORIO_MODELOS / "ensemble.pkl")
    print("  [OK] ensemble.pkl guardado")

    joblib.dump(PESOS_ENSEMBLE, DIRECTORIO_MODELOS / "ensemble_weights.pkl")
    print("  [OK] ensemble_weights.pkl guardado")

    with open(DIRECTORIO_METRICAS / "ensemble_metrics.json", "w") as f:
        json.dump(metricas, f, indent=2)
    print("  [OK] ensemble_metrics.json guardado")


def main():
    print("=" * 60)
    print("CREAR ENSEMBLE XGBOOST + LIGHTGBM")
    print("=" * 60)

    X_test, y_test = cargar_datos()
    modelo_xgb, modelo_lgb = cargar_modelos()
    metricas = crear_ensemble(modelo_xgb, modelo_lgb, X_test, y_test)
    guardar_ensemble(metricas)

    print("\n[OK] Ensemble creado exitosamente!")


if __name__ == "__main__":
    main()
