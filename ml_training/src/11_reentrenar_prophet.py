"""
Script 11: Re-entrenar Prophet correctamente
Entrena Prophet por producto individual (no agregado)
"""
import pandas as pd
import numpy as np
from prophet import Prophet
import joblib
import json
import time
import warnings
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
METRICS_DIR = BASE_DIR / "metrics"


def load_data():
    print("[1/5] Cargando dataset...")
    df = pd.read_csv(PROC_DIR / "dataset_entrenamiento.csv", parse_dates=["date"])
    print(f"  Filas: {df.shape[0]:,}")
    return df


def get_sample_products(df, n_products=50):
    """Selecciona productos representativos para entrenar Prophet."""
    print("\n[2/5] Seleccionando productos representativos...")
    product_stats = df.groupby("id")["y"].agg(["mean", "std", "count"]).reset_index()
    product_stats = product_stats[product_stats["count"] >= 100]
    
    product_stats["cv"] = product_stats["std"] / (product_stats["mean"] + 1)
    product_stats = product_stats.sort_values("cv", ascending=False)
    
    selected = product_stats["id"].values[:n_products]
    print(f"  Productos seleccionados: {len(selected)}")
    return selected


def train_prophet_per_product(df, product_ids):
    """Entrena Prophet para cada producto individualmente."""
    print("\n[3/5] Entrenando Prophet por producto...")
    t0 = time.time()
    
    all_predictions = []
    all_actuals = []
    trained_models = {}
    
    for i, product_id in enumerate(product_ids):
        product_df = df[df["id"] == product_id].copy()
        
        if len(product_df) < 100:
            continue
        
        product_df = product_df.sort_values("date")
        
        train_size = int(len(product_df) * 0.8)
        train_df = product_df[:train_size]
        test_df = product_df[train_size:]
        
        prophet_df = train_df[["date", "y"]].copy()
        prophet_df.columns = ["ds", "y"]
        prophet_df = prophet_df.groupby("ds")["y"].sum().reset_index()
        prophet_df = prophet_df.sort_values("ds")
        
        if len(prophet_df) < 30:
            continue
        
        try:
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                seasonality_mode="multiplicative",
                changepoint_prior_scale=0.05,
            )
            model.fit(prophet_df)
            
            test_prophet = test_df[["date", "y"]].copy()
            test_prophet.columns = ["ds", "y"]
            test_prophet = test_prophet.groupby("ds")["y"].sum().reset_index()
            test_prophet = test_prophet.sort_values("ds")
            
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            
            last_30 = min(30, len(test_prophet))
            y_actual = test_prophet["y"].values[:last_30]
            y_pred = forecast["yhat"].values[-last_30:]
            y_pred = np.maximum(y_pred, 0)
            
            all_predictions.extend(y_pred)
            all_actuals.extend(y_actual)
            
            trained_models[product_id] = model
            
            if (i + 1) % 10 == 0:
                print(f"  Procesados {i + 1}/{len(product_ids)} productos...")
                
        except Exception as e:
            print(f"  Error en producto {product_id}: {str(e)}")
            continue
    
    print(f"  Tiempo total: {time.time() - t0:.1f}s")
    return trained_models, np.array(all_predictions), np.array(all_actuals)


def calculate_metrics(y_actual, y_pred):
    """Calcula métricas de evaluación."""
    y_pred = np.maximum(y_pred, 0)
    
    mae = float(mean_absolute_error(y_actual, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_actual, y_pred)))
    r2 = float(r2_score(y_actual, y_pred))
    mape = float(np.mean(np.abs((y_actual - y_pred) / np.maximum(y_actual, 1))) * 100)
    
    return {
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "mape": mape
    }


def save_prophet_models(trained_models, metrics):
    """Guarda modelos de Prophet y métricas."""
    print("\n[4/5] Guardando modelos de Prophet...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    
    joblib.dump(trained_models, MODELS_DIR / "prophet_models_dict.pkl")
    
    metrics_data = {
        "modelo": "Prophet (entrenado por producto)",
        "n_productos_entrenados": len(trained_models),
        **metrics
    }
    
    with open(METRICS_DIR / "prophet_metrics_v2.json", "w") as f:
        json.dump(metrics_data, f, indent=2, default=str)
    
    print(f"  Modelos guardados: {MODELS_DIR / 'prophet_models_dict.pkl'}")
    print(f"  Métricas guardadas: {METRICS_DIR / 'prophet_metrics_v2.json'}")


def main():
    print("=" * 60)
    print("RE-ENTRENAMIENTO DE PROPHET (POR PRODUCTO)")
    print("=" * 60)
    
    df = load_data()
    product_ids = get_sample_products(df, n_products=50)
    trained_models, y_pred, y_actual = train_prophet_per_product(df, product_ids)
    
    if len(y_actual) == 0:
        print("\n[ERROR] No se pudieron generar predicciones")
        return
    
    metrics = calculate_metrics(y_actual, y_pred)
    
    print("\n[5/5] Métricas de Prophet:")
    print(f"  MAE:  {metrics['mae']:.4f}")
    print(f"  RMSE: {metrics['rmse']:.4f}")
    print(f"  R2:   {metrics['r2']:.4f}")
    print(f"  MAPE: {metrics['mape']:.2f}%")
    
    save_prophet_models(trained_models, metrics)
    
    print("\n" + "=" * 60)
    print("COMPARACIÓN CON XGBOOST Y LIGHTGBM")
    print("=" * 60)
    
    xgb_metrics = {"mae": 1.6271, "rmse": 3.5007, "r2": 0.7268, "mape": 69.71}
    lgb_metrics = {"mae": 1.6279, "rmse": 3.5017, "r2": 0.7266, "mape": 69.52}
    
    print(f"\n  {'Modelo':<20} {'MAE':>8} {'RMSE':>8} {'R²':>8} {'MAPE':>8}")
    print(f"  {'-'*52}")
    print(f"  {'XGBoost v2':<20} {xgb_metrics['mae']:>8.4f} {xgb_metrics['rmse']:>8.4f} {xgb_metrics['r2']:>8.4f} {xgb_metrics['mape']:>7.2f}%")
    print(f"  {'LightGBM v2':<20} {lgb_metrics['mae']:>8.4f} {lgb_metrics['rmse']:>8.4f} {lgb_metrics['r2']:>8.4f} {lgb_metrics['mape']:>7.2f}%")
    print(f"  {'Prophet (corregido)':<20} {metrics['mae']:>8.4f} {metrics['rmse']:>8.4f} {metrics['r2']:>8.4f} {metrics['mape']:>7.2f}%")
    
    print(f"\n[OK] Re-entrenamiento de Prophet completado!")


if __name__ == "__main__":
    main()
