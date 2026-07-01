"""
Script 08: Generar predicciones con modelos entrenados
Entrada: models/*.pkl, producto_id, horizonte
Salida: predicciones en CSV
"""
import pandas as pd
import numpy as np
import joblib
import yaml
import json
import argparse
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"

with open(BASE_DIR / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

FEATURE_COLS = [
    "price", "dayofweek", "month", "is_month_end",
    "lag_1", "lag_7", "lag_14", "lag_28",
    "rolling_mean_7", "rolling_mean_14", "rolling_mean_28",
    "rolling_std_7", "rolling_std_28",
    "price_change_1",
    "is_holiday", "month_sin", "dayofweek_sin",
    "rolling_max_28", "rolling_min_28",
]


def load_model(model_name):
    path = MODELS_DIR / f"{model_name}_model.pkl"
    if not path.exists():
        print(f"[ERROR] Modelo no encontrado: {path}")
        return None
    return joblib.load(path)


def get_product_history(df, item_id):
    product_df = df[df["item_id"] == item_id].sort_values("date").copy()
    if product_df.empty:
        return None
    return product_df


def predict_demand(model, product_df, horizonte):
    last_features = product_df[FEATURE_COLS].iloc[-1:].copy()

    predicciones = []
    last_row = product_df.iloc[-1].copy()
    last_row["date"] = pd.to_datetime(last_row["date"])

    for day in range(1, horizonte + 1):
        features_input = last_row[FEATURE_COLS].values.reshape(1, -1).astype(float)
        features_df = pd.DataFrame(features_input, columns=FEATURE_COLS)

        pred = model.predict(features_df)[0]
        pred = max(0, round(float(pred)))

        new_date = last_row["date"] + pd.Timedelta(days=1)

        predicciones.append({
            "dia": day,
            "fecha": str(new_date.date()) if hasattr(new_date, "date") else str(new_date),
            "demanda_estimada": pred,
        })

        last_row["y"] = pred
        last_row["lag_28"] = last_row.get("lag_14", 0)
        last_row["lag_14"] = last_row.get("lag_7", 0)
        last_row["lag_7"] = last_row.get("lag_1", 0)
        last_row["lag_1"] = pred
        last_row["date"] = new_date

    return predicciones


def main():
    parser = argparse.ArgumentParser(description="Predecir demanda con modelos ML")
    parser.add_argument("--producto", type=str, required=True, help="Item ID del producto (ej: FOODS_3_090)")
    parser.add_argument("--horizonte", type=int, default=30, help="Dias a predecir (default: 30)")
    parser.add_argument("--modelo", type=str, default="xgboost", choices=["xgboost", "lightgbm"],
                        help="Modelo a usar")
    args = parser.parse_args()

    print("=" * 60)
    print("GENERAR PREDICCIONES DE DEMANDA")
    print("=" * 60)
    print(f"  Producto: {args.producto}")
    print(f"  Horizonte: {args.horizonte} dias")
    print(f"  Modelo: {args.modelo.upper()}")

    model = load_model(args.modelo)
    if model is None:
        return

    print("\n[1/3] Cargando historial del producto...")
    df = pd.read_csv(PROC_DIR / "dataset_entrenamiento.csv")
    product_df = get_product_history(df, args.producto)

    if product_df is None:
        print(f"  [ERROR] Producto '{args.producto}' no encontrado en el dataset.")
        print(f"  Productos disponibles (muestra): {df['item_id'].unique()[:10].tolist()}")
        return

    print(f"  Historial: {len(product_df)} dias")
    print(f"  Rango: {product_df['date'].min()} a {product_df['date'].max()}")
    print(f"  Demanda promedio: {product_df['y'].mean():.2f} unidades/dia")

    print(f"\n[2/3] Prediciendo demanda para {args.horizonte} dias...")
    t0 = time.time()
    predicciones = predict_demand(model, product_df, args.horizonte)
    print(f"  Tiempo: {time.time() - t0:.2f}s")

    print(f"\n[3/3] Resultados:")
    print(f"  {'Dia':<6} {'Fecha':<15} {'Demanda Estimada':>15}")
    print(f"  {'-'*40}")
    total = 0
    for p in predicciones:
        print(f"  {p['dia']:<6} {p['fecha']:<15} {p['demanda_estimada']:>15}")
        total += p["demanda_estimada"]

    print(f"  {'-'*40}")
    print(f"  {'TOTAL':<21} {total:>15}")
    print(f"  {'PROMEDIO/DIA':<21} {total/args.horizonte:>15.1f}")

    output_path = BASE_DIR / f"prediccion_{args.producto}_{args.modelo}.csv"
    pd.DataFrame(predicciones).to_csv(output_path, index=False)
    print(f"\n  Predicciones guardadas en: {output_path}")

    result_for_api = {
        "producto": args.producto,
        "modelo": args.modelo,
        "horizonte": args.horizonte,
        "predicciones": predicciones,
        "total_estimado": total,
        "promedio_diario": round(total / args.horizonte, 1),
    }
    api_path = BASE_DIR / "metrics" / "ultima_prediccion.json"
    with open(api_path, "w") as f:
        json.dump(result_for_api, f, indent=2)
    print(f"  JSON para API: {api_path}")

    print("\n[OK] Prediccion completada!")


if __name__ == "__main__":
    main()
