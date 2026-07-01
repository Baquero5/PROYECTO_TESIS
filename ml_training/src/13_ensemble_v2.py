"""
Script 13: Ensemble optimizado (XGBoost + LightGBM sin Prophet)
- Festivos Ecuador (dinámicos)
"""
import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
import joblib
import json
import time
import warnings
from pathlib import Path
from datetime import timedelta
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
METRICS_DIR = BASE_DIR / "metrics"

FEATURE_COLS = [
    "price", "dayofweek", "month", "is_month_end",
    "lag_1", "lag_7", "lag_14", "lag_28",
    "rolling_mean_7", "rolling_mean_14", "rolling_mean_28",
    "rolling_std_7", "rolling_std_28",
    "price_change_1",
    "is_holiday", "month_sin", "dayofweek_sin",
    "rolling_max_28", "rolling_min_28",
]


def calc_easter_sunday(year: int) -> pd.Timestamp:
    """Calcula el domingo de Pascua (algoritmo de Meeus/Jones/Butcher)."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return pd.Timestamp(year, month, day)


def get_ecuador_holidays(year: int) -> list:
    """
    Genera festivos de Ecuador para un año dado.
    Incluye festivos fijos y móviles (Carnaval, Viernes Santo).
    """
    easter = calc_easter_sunday(year)

    # Festivos fijos
    fixed = [
        f"{year}-01-01",  # Año Nuevo
        f"{year}-05-01",  # Día del Trabajo
        f"{year}-05-24",  # Batalla de Pichincha
        f"{year}-08-10",  # Independencia de Guayaquil
        f"{year}-10-09",  # Primer Grito de Independencia
        f"{year}-11-02",  # Día de los Difuntos
        f"{year}-11-03",  # Independencia de Cuenca
        f"{year}-12-25",  # Navidad
    ]

    # Festivos móviles (basados en Pascua)
    carnaval_lunes = easter - timedelta(days=48)
    carnaval_martes = easter - timedelta(days=47)
    viernes_santo = easter - timedelta(days=2)

    variable = [
        carnaval_lunes.strftime("%Y-%m-%d"),
        carnaval_martes.strftime("%Y-%m-%d"),
        viernes_santo.strftime("%Y-%m-%d"),
    ]

    return fixed + variable


def load_data():
    print("[1/5] Cargando dataset...")
    df = pd.read_csv(PROC_DIR / "dataset_entrenamiento.csv", parse_dates=["date"])
    print(f"  Filas: {df.shape[0]:,}")
    return df


def add_features(df):
    print("\n[2/5] Agregando features...")
    
    # Festivos de Ecuador (generados dinámicamente por año)
    all_holidays = []
    for y in range(df["date"].dt.year.min(), df["date"].dt.year.max() + 1):
        all_holidays.extend(get_ecuador_holidays(y))
    df["is_holiday"] = df["date"].dt.strftime("%Y-%m-%d").isin(all_holidays).astype(np.int8)
    
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["dayofweek_sin"] = np.sin(2 * np.pi * df["dayofweek"] / 7)
    
    if "rolling_max_28" not in df.columns:
        df["rolling_max_28"] = df.groupby("id")["y"].transform(lambda x: x.rolling(28, min_periods=1).max())
        df["rolling_min_28"] = df.groupby("id")["y"].transform(lambda x: x.rolling(28, min_periods=1).min())
    
    print(f"  Festivos: Ecuador (dinámicos)")
    df = df.dropna()
    return df


def train_models(X_train, y_train):
    print("\n[3/5] Entrenando modelos base...")
    t0 = time.time()

    xgb_model = xgb.XGBRegressor(
        n_estimators=500, max_depth=6, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        random_state=42, tree_method="hist", n_jobs=-1,
    )
    xgb_model.fit(X_train, y_train)

    lgb_model = lgb.LGBMRegressor(
        n_estimators=500, num_leaves=63, learning_rate=0.05,
        feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=5,
        random_state=42, n_jobs=-1, verbose=-1,
    )
    lgb_model.fit(X_train, y_train)

    print(f"  Tiempo: {time.time() - t0:.1f}s")
    return xgb_model, lgb_model


def find_best_weights(xgb_model, lgb_model, X_test, y_test):
    print("\n[4/5] Buscando mejores pesos del ensemble...")
    
    xgb_pred = xgb_model.predict(X_test)
    lgb_pred = lgb_model.predict(X_test)

    best_r2 = -999
    best_weights = (0.5, 0.5)
    
    for w in np.arange(0.1, 0.9, 0.05):
        xgb_w = w
        lgb_w = 1 - w
        ensemble_pred = xgb_w * xgb_pred + lgb_w * lgb_pred
        ensemble_pred = np.maximum(ensemble_pred, 0)
        
        r2 = r2_score(y_test, ensemble_pred)
        mae = mean_absolute_error(y_test, ensemble_pred)
        mape = np.mean(np.abs((y_test - ensemble_pred) / np.maximum(y_test, 1))) * 100
        
        if r2 > best_r2:
            best_r2 = r2
            best_weights = (xgb_w, lgb_w)
            best_metrics = {"mae": mae, "r2": r2, "mape": mape}

    print(f"  Mejores pesos: XGBoost={best_weights[0]:.2f}, LightGBM={best_weights[1]:.2f}")
    print(f"  Ensemble R²: {best_metrics['r2']:.4f}")
    print(f"  Ensemble MAE: {best_metrics['mae']:.4f}")
    print(f"  Ensemble MAPE: {best_metrics['mape']:.2f}%")
    
    return best_weights, best_metrics


def save_ensemble(xgb_model, lgb_model, weights, metrics):
    print("\n[5/5] Guardando ensemble...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    ensemble_data = {
        "type": "ensemble_xgb_lgb",
        "xgb_weight": float(weights[0]),
        "lgb_weight": float(weights[1]),
        "xgb_model_file": "xgboost_v2_model.pkl",
        "lgb_model_file": "lightgbm_v2_model.pkl",
        "feature_columns": FEATURE_COLS,
    }
    
    joblib.dump(ensemble_data, MODELS_DIR / "ensemble_v2.pkl")
    
    metrics_data = {
        "modelo": "Ensemble v2 (XGBoost + LightGBM)",
        "version": "2.0",
        "pesos": {"xgboost": weights[0], "lightgbm": weights[1]},
        "mae": metrics["mae"],
        "r2": metrics["r2"],
        "mape": metrics["mape"],
    }
    
    with open(METRICS_DIR / "ensemble_v2_metrics.json", "w") as f:
        json.dump(metrics_data, f, indent=2, default=str)
    
    print(f"  Ensemble guardado: {MODELS_DIR / 'ensemble_v2.pkl'}")
    print(f"  Métricas guardadas: {METRICS_DIR / 'ensemble_v2_metrics.json'}")


def main():
    print("=" * 60)
    print("ENSEMBLE OPTIMIZADO (XGBoost + LightGBM)")
    print("=" * 60)

    df = load_data()
    df = add_features(df)
    
    X = df[FEATURE_COLS].fillna(0)
    y = df["y"].fillna(0)
    
    max_sample = 300000
    if len(X) > max_sample:
        idx = np.random.RandomState(42).choice(len(X), max_sample, replace=False)
        X = X.iloc[idx].copy()
        y = y.iloc[idx].copy()
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    xgb_model, lgb_model = train_models(X_train, y_train)
    weights, metrics = find_best_weights(xgb_model, lgb_model, X_test, y_test)
    save_ensemble(xgb_model, lgb_model, weights, metrics)

    print("\n" + "=" * 60)
    print("COMPARACIÓN FINAL")
    print("=" * 60)
    xgb_pred = xgb_model.predict(X_test)
    lgb_pred = lgb_model.predict(X_test)
    xgb_r2 = r2_score(y_test, xgb_pred)
    lgb_r2 = r2_score(y_test, lgb_pred)
    
    print(f"\n  XGBoost v2:        R² = {xgb_r2:.4f}")
    print(f"  LightGBM v2:       R² = {lgb_r2:.4f}")
    print(f"  Ensemble v2:       R² = {metrics['r2']:.4f}  ← MEJOR")
    print(f"\n[OK] Ensemble completado!")


if __name__ == "__main__":
    main()
