"""
Script 06: Entrenar modelo LightGBM
Entrada: data/processed/dataset_entrenamiento.csv
Salida: models/lightgbm_model.pkl
"""
import pandas as pd
import numpy as np
import lightgbm as lgb
import joblib
import yaml
import json
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

PARAMS_LGB = config["modelos"]["lightgbm"]
COLUMNAS_FEATURES = config["features"]


def cargar_datos():
    print("[1/4] Cargando dataset de entrenamiento...")
    df = pd.read_csv(DIRECTORIO_PROCESADO / "dataset_entrenamiento.csv")
    print(f"  Filas: {df.shape[0]:,} | Columnas: {df.shape[1]}")
    return df


def preparar_features(df):
    print("\n[2/4] Preparando features...")
    X = df[COLUMNAS_FEATURES].copy()
    y = df["y"].copy()

    X = X.fillna(0)
    y = y.fillna(0)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"  Train: {X_train.shape[0]:,} muestras")
    print(f"  Test: {X_test.shape[0]:,} muestras")
    print(f"  Features: {X_train.shape[1]}")

    return X_train, X_test, y_train, y_test


def entrenar_modelo(X_train, y_train, X_test, y_test):
    print("\n[3/4] Entrenando LightGBM...")
    t0 = time.time()

    params = {
        "objective": "regression",
        "metric": "rmse",
        "n_estimators": PARAMS_LGB["n_estimators"],
        "num_leaves": PARAMS_LGB["num_leaves"],
        "learning_rate": PARAMS_LGB["learning_rate"],
        "feature_fraction": PARAMS_LGB["feature_fraction"],
        "bagging_fraction": PARAMS_LGB["bagging_fraction"],
        "bagging_freq": PARAMS_LGB["bagging_freq"],
        "random_state": PARAMS_LGB["random_state"],
        "verbose": -1,
    }

    modelo = lgb.LGBMRegressor(**params)
    modelo.fit(
        X_train, y_train,
        eval_set=[(X_train, y_train), (X_test, y_test)],
        callbacks=[lgb.log_evaluation(50)],
    )

    print(f"  Tiempo de entrenamiento: {time.time() - t0:.1f}s")
    return modelo


def evaluar_modelo(modelo, X_test, y_test):
    print("\n[4/4] Evaluando modelo...")
    y_pred = modelo.predict(X_test)
    y_pred = np.maximum(y_pred, 0)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 1))) * 100

    metricas = {
        "modelo": "LightGBM",
        "version": "1.0",
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "r2": round(float(r2), 4),
        "mape": round(float(mape), 4),
        "features_used": COLUMNAS_FEATURES,
    }

    print(f"  MAE:  {mae:.4f}")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  R2:   {r2:.4f}")
    print(f"  MAPE: {mape:.4f}%")

    return metricas, y_pred


def guardar_modelo(modelo, metricas):
    DIRECTORIO_MODELOS.mkdir(parents=True, exist_ok=True)
    DIRECTORIO_METRICAS.mkdir(parents=True, exist_ok=True)

    ruta_modelo = DIRECTORIO_MODELOS / "lightgbm_model.pkl"
    joblib.dump(modelo, ruta_modelo)
    print(f"\n  Modelo guardado: {ruta_modelo}")

    ruta_metricas = DIRECTORIO_METRICAS / "lightgbm_metrics.json"
    with open(ruta_metricas, "w") as f:
        json.dump(metricas, f, indent=2)
    print(f"  Metricas guardadas: {ruta_metricas}")


def main():
    print("=" * 60)
    print("ENTRENAR MODELO LIGHTGBM")
    print("=" * 60)

    df = cargar_datos()
    X_train, X_test, y_train, y_test = preparar_features(df)
    modelo = entrenar_modelo(X_train, y_train, X_test, y_test)
    metricas, y_pred = evaluar_modelo(modelo, X_test, y_test)
    guardar_modelo(modelo, metricas)

    print("\n[OK] LightGBM entrenado y guardado exitosamente!")


if __name__ == "__main__":
    main()
