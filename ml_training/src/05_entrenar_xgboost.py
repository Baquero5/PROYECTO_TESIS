"""
Script 05: Entrenar modelo XGBoost
Entrada: data/processed/dataset_entrenamiento.csv
Salida: models/xgboost_model.pkl
"""
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import yaml
import json
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

XGB_PARAMS = config["modelos"]["xgboost"]

FEATURE_COLS = [
    "price", "dayofweek", "month", "is_month_end",
    "lag_1", "lag_7", "lag_14", "lag_28",
    "rolling_mean_7", "rolling_mean_14", "rolling_mean_28",
    "rolling_std_7", "rolling_std_28",
    "price_change_1",
    "is_holiday", "month_sin", "dayofweek_sin",
    "rolling_max_28", "rolling_min_28",
]


def load_data():
    print("[1/4] Cargando dataset de entrenamiento...")
    df = pd.read_csv(PROC_DIR / "dataset_entrenamiento.csv")
    print(f"  Filas: {df.shape[0]:,} | Columnas: {df.shape[1]}")
    return df


def prepare_features(df):
    print("\n[2/4] Preparando features...")
    X = df[FEATURE_COLS].copy()
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


def train_model(X_train, y_train):
    print("\n[3/4] Entrenando XGBoost...")
    t0 = time.time()

    model = xgb.XGBRegressor(
        n_estimators=XGB_PARAMS["n_estimators"],
        max_depth=XGB_PARAMS["max_depth"],
        learning_rate=XGB_PARAMS["learning_rate"],
        subsample=XGB_PARAMS["subsample"],
        colsample_bytree=XGB_PARAMS["colsample_bytree"],
        random_state=XGB_PARAMS["random_state"],
        tree_method="hist",
        n_jobs=-1,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_train, y_train)],
        verbose=50,
    )

    print(f"  Tiempo de entrenamiento: {time.time() - t0:.1f}s")
    return model


def evaluate_model(model, X_test, y_test):
    print("\n[4/4] Evaluando modelo...")
    y_pred = model.predict(X_test)
    y_pred = np.maximum(y_pred, 0)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 1))) * 100

    metrics = {
        "modelo": "XGBoost",
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "r2": round(float(r2), 4),
        "mape": round(float(mape), 4),
        "features_used": FEATURE_COLS,
    }

    print(f"  MAE:  {mae:.4f}")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  R2:   {r2:.4f}")
    print(f"  MAPE: {mape:.4f}%")

    return metrics, y_pred


def save_model(model, metrics):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    model_path = MODELS_DIR / "xgboost_model.pkl"
    joblib.dump(model, model_path)
    print(f"\n  Modelo guardado: {model_path}")

    metrics_path = METRICS_DIR / "xgboost_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"  Metricas guardadas: {metrics_path}")


def main():
    print("=" * 60)
    print("ENTRENAR MODELO XGBOOST")
    print("=" * 60)

    df = load_data()
    X_train, X_test, y_train, y_test = prepare_features(df)
    model = train_model(X_train, y_train)
    metrics, y_pred = evaluate_model(model, X_test, y_test)
    save_model(model, metrics)

    print("\n[OK] XGBoost entrenado y guardado exitosamente!")


if __name__ == "__main__":
    main()
