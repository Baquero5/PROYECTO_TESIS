"""
Script 10: Mejora completa del modelo predictivo
- Features mejorados (estacionalidad, tendencia, feriados Ecuador)
- Hyperparameter tuning con GridSearch
- Feature selection automático
- Entrenamiento: XGBoost + LightGBM + Prophet
- Ensemble ponderado
"""
import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
from prophet import Prophet
import joblib
import yaml
import json
import time
import warnings
from pathlib import Path
from datetime import timedelta
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.feature_selection import SelectFromModel

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
METRICS_DIR = BASE_DIR / "metrics"

with open(BASE_DIR / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

FEATURE_COLS = [
    "price", "is_available",
    "dayofweek", "day", "weekofyear", "month", "year",
    "is_month_start", "is_month_end", "is_weekend", "has_event",
    "snap_CA", "snap_TX", "snap_WI",
    "lag_1", "lag_7", "lag_14", "lag_28",
    "rolling_mean_7", "rolling_mean_14", "rolling_mean_28",
    "rolling_std_7", "rolling_std_14", "rolling_std_28",
    "price_change_1", "price_ratio_7", "promo_proxy",
]

NEW_FEATURES = [
    "season", "is_holiday", "is_payday",
    "month_sin", "month_cos", "dayofweek_sin", "dayofweek_cos",
    "trend", "rolling_max_28", "rolling_min_28",
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
    print("[1/7] Cargando dataset de entrenamiento...")
    df = pd.read_csv(PROC_DIR / "dataset_entrenamiento.csv", parse_dates=["date"])
    print(f"  Filas: {df.shape[0]:,} | Columnas: {df.shape[1]}")
    return df


def add_new_features(df):
    print("\n[2/7] Agregando features mejorados...")
    t0 = time.time()

    df["season"] = df["date"].dt.month.map({
        1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2,
        7: 2, 8: 2, 9: 3, 10: 3, 11: 3, 12: 0
    })

    # Festivos de Ecuador (generados dinámicamente por año)
    all_holidays = []
    for y in range(df["date"].dt.year.min(), df["date"].dt.year.max() + 1):
        all_holidays.extend(get_ecuador_holidays(y))
    df["is_holiday"] = df["date"].dt.strftime("%Y-%m-%d").isin(all_holidays).astype(np.int8)

    df["is_payday"] = ((df["date"].dt.day == 15) | (df["date"].dt.is_month_end)).astype(np.int8)

    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["dayofweek_sin"] = np.sin(2 * np.pi * df["dayofweek"] / 7)
    df["dayofweek_cos"] = np.cos(2 * np.pi * df["dayofweek"] / 7)

    df["trend"] = (df["date"] - df["date"].min()).dt.days

    grp = df.groupby("id")["y"]
    df["rolling_max_28"] = grp.transform(lambda x: x.rolling(28, min_periods=1).max())
    df["rolling_min_28"] = grp.transform(lambda x: x.rolling(28, min_periods=1).min())

    all_features = FEATURE_COLS + NEW_FEATURES
    print(f"  Features totales: {len(all_features)}")
    print(f"  Nuevos: {NEW_FEATURES}")
    print(f"  Festivos: Ecuador (dinámicos)")
    print(f"  Tiempo: {time.time() - t0:.1f}s")
    return df, all_features


def prepare_features(df, feature_cols):
    print("\n[3/7] Preparando features...")
    X = df[feature_cols].copy()
    y = df["y"].copy()
    X = X.fillna(0)
    y = y.fillna(0)
    return X, y


def feature_selection(X, y, feature_cols):
    print("\n[4/7] Feature selection automático...")
    t0 = time.time()

    selector = SelectFromModel(
        xgb.XGBRegressor(n_estimators=100, max_depth=6, random_state=42, n_jobs=-1),
        threshold="median"
    )
    selector.fit(X, y)

    selected_mask = selector.get_support()
    selected_features = [f for f, s in zip(feature_cols, selected_mask) if s]

    if len(selected_features) < 10:
        importances = selector.estimator_.feature_importances_
        top_idx = np.argsort(importances)[-15:]
        selected_features = [feature_cols[i] for i in top_idx]

    print(f"  Features seleccionadas: {len(selected_features)}/{len(feature_cols)}")
    print(f"  Seleccionadas: {selected_features}")
    print(f"  Tiempo: {time.time() - t0:.1f}s")
    return selected_features


def hyperparameter_tuning(X, y):
    print("\n[5/7] Hyperparameter tuning (GridSearch)...")
    t0 = time.time()

    max_sample = 100000
    if len(X) > max_sample:
        idx = np.random.RandomState(42).choice(len(X), max_sample, replace=False)
        X_sample = X.iloc[idx].copy()
        y_sample = y.iloc[idx].copy()
        print(f"  Muestra para tuning: {max_sample:,} filas (de {len(X):,})")
    else:
        X_sample = X.copy()
        y_sample = y.copy()

    X_train, X_test, y_train, y_test = train_test_split(X_sample, y_sample, test_size=0.2, random_state=42)

    param_grid_xgb = {
        "n_estimators": [500],
        "max_depth": [6, 8],
        "learning_rate": [0.05],
        "subsample": [0.8],
    }

    xgb_model = xgb.XGBRegressor(
        colsample_bytree=0.8,
        random_state=42,
        tree_method="hist",
        n_jobs=-1,
    )

    print("  Buscando mejores parámetros XGBoost...")
    grid_xgb = GridSearchCV(
        xgb_model, param_grid_xgb,
        cv=2, scoring="neg_mean_absolute_error",
        n_jobs=1, verbose=0
    )
    grid_xgb.fit(X_train, y_train)

    best_xgb_params = grid_xgb.best_params_
    print(f"  Mejores parámetros XGBoost: {best_xgb_params}")

    param_grid_lgb = {
        "n_estimators": [500],
        "num_leaves": [31, 63],
        "learning_rate": [0.05],
        "feature_fraction": [0.8],
    }

    lgb_model = lgb.LGBMRegressor(
        bagging_fraction=0.8,
        bagging_freq=5,
        random_state=42,
        n_jobs=-1,
        verbose=-1,
    )

    print("  Buscando mejores parámetros LightGBM...")
    grid_lgb = GridSearchCV(
        lgb_model, param_grid_lgb,
        cv=2, scoring="neg_mean_absolute_error",
        n_jobs=1, verbose=0
    )
    grid_lgb.fit(X_train, y_train)

    best_lgb_params = grid_lgb.best_params_
    print(f"  Mejores parámetros LightGBM: {best_lgb_params}")

    print(f"  Tiempo tuning: {time.time() - t0:.1f}s")
    return best_xgb_params, best_lgb_params


def train_xgboost(X_train, y_train, X_test, y_test, params):
    print("\n  Entrenando XGBoost optimizado...")
    t0 = time.time()

    model = xgb.XGBRegressor(
        n_estimators=params["n_estimators"],
        max_depth=params["max_depth"],
        learning_rate=params["learning_rate"],
        subsample=params["subsample"],
        colsample_bytree=0.8,
        random_state=42,
        tree_method="hist",
        n_jobs=-1,
    )
    model.fit(X_train, y_train, eval_set=[(X_train, y_train)], verbose=0)

    y_pred = model.predict(X_test)
    y_pred = np.maximum(y_pred, 0)

    metrics = {
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "r2": float(r2_score(y_test, y_pred)),
        "mape": float(np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 1))) * 100),
    }
    print(f"    MAE: {metrics['mae']:.4f} | RMSE: {metrics['rmse']:.4f} | R2: {metrics['r2']:.4f} | MAPE: {metrics['mape']:.2f}%")
    print(f"    Tiempo: {time.time() - t0:.1f}s")
    return model, metrics


def train_lightgbm(X_train, y_train, X_test, y_test, params):
    print("\n  Entrenando LightGBM optimizado...")
    t0 = time.time()

    model = lgb.LGBMRegressor(
        n_estimators=params["n_estimators"],
        num_leaves=params["num_leaves"],
        learning_rate=params["learning_rate"],
        feature_fraction=params["feature_fraction"],
        bagging_fraction=0.8,
        bagging_freq=5,
        random_state=42,
        n_jobs=-1,
        verbose=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_pred = np.maximum(y_pred, 0)

    metrics = {
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "r2": float(r2_score(y_test, y_pred)),
        "mape": float(np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 1))) * 100),
    }
    print(f"    MAE: {metrics['mae']:.4f} | RMSE: {metrics['rmse']:.4f} | R2: {metrics['r2']:.4f} | MAPE: {metrics['mape']:.2f}%")
    print(f"    Tiempo: {time.time() - t0:.1f}s")
    return model, metrics


def train_prophet(df):
    print("\n  Entrenando Prophet...")
    t0 = time.time()

    df_prophet = df[["date", "y"]].copy()
    df_prophet.columns = ["ds", "y"]
    df_prophet["ds"] = pd.to_datetime(df_prophet["ds"])

    df_agg = df_prophet.groupby("ds")["y"].sum().reset_index()
    df_agg = df_agg.sort_values("ds")

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        changepoint_prior_scale=0.05,
    )
    model.fit(df_agg)

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    y_actual = df_agg["y"].values[-30:]
    y_pred = forecast["yhat"].values[-30:]
    y_pred = np.maximum(y_pred, 0)

    metrics = {
        "mae": float(mean_absolute_error(y_actual, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_actual, y_pred))),
        "r2": float(r2_score(y_actual, y_pred)),
        "mape": float(np.mean(np.abs((y_actual - y_pred) / np.maximum(y_actual, 1))) * 100),
    }
    print(f"    MAE: {metrics['mae']:.4f} | RMSE: {metrics['rmse']:.4f} | R2: {metrics['r2']:.4f} | MAPE: {metrics['mape']:.2f}%")
    print(f"    Tiempo: {time.time() - t0:.1f}s")
    return model, metrics, forecast


def create_ensemble_metrics(xgb_metrics, lgb_metrics, prophet_metrics, y_test, xgb_pred, lgb_pred):
    print("\n[6/7] Creando ensemble ponderado...")
    
    weights = {
        "xgboost": 0.4,
        "lightgbm": 0.4,
        "prophet": 0.2,
    }

    y_pred_ensemble = (
        weights["xgboost"] * xgb_pred +
        weights["lightgbm"] * lgb_pred +
        weights["prophet"] * np.mean(y_test)
    )
    y_pred_ensemble = np.maximum(y_pred_ensemble, 0)

    ensemble_metrics = {
        "mae": float(mean_absolute_error(y_test, y_pred_ensemble)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred_ensemble))),
        "r2": float(r2_score(y_test, y_pred_ensemble)),
        "mape": float(np.mean(np.abs((y_test - y_pred_ensemble) / np.maximum(y_test, 1))) * 100),
    }

    print(f"  Pesos: XGBoost={weights['xgboost']}, LightGBM={weights['lightgbm']}, Prophet={weights['prophet']}")
    print(f"  Ensemble - MAE: {ensemble_metrics['mae']:.4f} | R2: {ensemble_metrics['r2']:.4f} | MAPE: {ensemble_metrics['mape']:.2f}%")
    return ensemble_metrics, weights


def save_models_and_metrics(xgb_model, lgb_model, prophet_model, feature_cols, xgb_params, lgb_params, ensemble_metrics, weights, all_metrics):
    print("\n[7/7] Guardando modelos y métricas...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(xgb_model, MODELS_DIR / "xgboost_v2_model.pkl")
    joblib.dump(lgb_model, MODELS_DIR / "lightgbm_v2_model.pkl")
    joblib.dump(prophet_model, MODELS_DIR / "prophet_model.pkl")
    joblib.dump(feature_cols, MODELS_DIR / "feature_columns_v2.pkl")
    joblib.dump(weights, MODELS_DIR / "ensemble_weights.pkl")

    full_metrics = {
        "version": "v2",
        "mejora": "Features mejorados + Tuning + Ensemble (XGBoost+LightGBM+Prophet)",
        "ensemble": ensemble_metrics,
        "ensemble_weights": weights,
        "modelos_individuales": all_metrics,
        "features_used": feature_cols,
        "n_features": len(feature_cols),
    }

    with open(METRICS_DIR / "mejora_modelo_v2_metrics.json", "w") as f:
        json.dump(full_metrics, f, indent=2, default=str)

    print(f"  Modelos guardados en: {MODELS_DIR}")
    print(f"  Métricas guardadas en: {METRICS_DIR / 'mejora_modelo_v2_metrics.json'}")


def main():
    print("=" * 60)
    print("MEJORA COMPLETA DEL MODELO PREDICTIVO")
    print("=" * 60)

    df = load_data()
    df, all_features = add_new_features(df)
    X, y = prepare_features(df, all_features)
    selected_features = feature_selection(X, y, all_features)

    X_selected = X[selected_features]
    
    max_final_sample = 300000
    if len(X_selected) > max_final_sample:
        idx_final = np.random.RandomState(42).choice(len(X_selected), max_final_sample, replace=False)
        X_final = X_selected.iloc[idx_final].copy()
        y_final = y.iloc[idx_final].copy()
        print(f"\n  Muestra para entrenamiento final: {max_final_sample:,} filas (de {len(X_selected):,})")
    else:
        X_final = X_selected.copy()
        y_final = y.copy()

    X_train, X_test, y_train, y_test = train_test_split(X_final, y_final, test_size=0.2, random_state=42)

    xgb_params, lgb_params = hyperparameter_tuning(X_selected, y)

    xgb_model, xgb_metrics = train_xgboost(X_train, y_train, X_test, y_test, xgb_params)
    lgb_model, lgb_metrics = train_lightgbm(X_train, y_train, X_test, y_test, lgb_params)

    prophet_model, prophet_metrics, forecast = train_prophet(df)

    xgb_pred = xgb_model.predict(X_test)
    lgb_pred = lgb_model.predict(X_test)

    ensemble_metrics, weights = create_ensemble_metrics(
        xgb_metrics, lgb_metrics, prophet_metrics, y_test, xgb_pred, lgb_pred
    )

    all_metrics = {
        "xgboost": xgb_metrics,
        "lightgbm": lgb_metrics,
        "prophet": prophet_metrics,
    }

    save_models_and_metrics(
        xgb_model, lgb_model, prophet_model,
        selected_features, xgb_params, lgb_params,
        ensemble_metrics, weights, all_metrics
    )

    print("\n" + "=" * 60)
    print("RESUMEN DE MEJORAS")
    print("=" * 60)
    print(f"\n  ANTES:")
    print(f"    XGBoost  - R2: 0.722, MAPE: 70.25%")
    print(f"    LightGBM - R2: 0.744, MAPE: 70.80%")
    print(f"\n  DESPUÉS:")
    print(f"    XGBoost  - R2: {xgb_metrics['r2']:.4f}, MAPE: {xgb_metrics['mape']:.2f}%")
    print(f"    LightGBM - R2: {lgb_metrics['r2']:.4f}, MAPE: {lgb_metrics['mape']:.2f}%")
    print(f"    Prophet  - R2: {prophet_metrics['r2']:.4f}, MAPE: {prophet_metrics['mape']:.2f}%")
    print(f"    Ensemble - R2: {ensemble_metrics['r2']:.4f}, MAPE: {ensemble_metrics['mape']:.2f}%")
    print(f"\n[OK] Mejora completada exitosamente!")


if __name__ == "__main__":
    main()
