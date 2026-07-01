"""
Script 07: Evaluar y comparar modelos XGBoost vs LightGBM
Entrada: models/*.pkl
Salida: metrics/comparativa_modelos.json, metrics/reporte_metricas.txt, metrics/*.png
"""
import pandas as pd
import numpy as np
import joblib
import json
import time
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

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


def load_data_and_split():
    print("[1/5] Cargando dataset...")
    df = pd.read_csv(PROC_DIR / "dataset_entrenamiento.csv")
    X = df[FEATURE_COLS].fillna(0)
    y = df["y"].fillna(0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"  Test: {X_test.shape[0]:,} muestras")
    return X_test, y_test, X_train, y_train


def load_models():
    print("\n[2/5] Cargando modelos entrenados...")
    models = {}
    for name in ["xgboost", "lightgbm"]:
        path = MODELS_DIR / f"{name}_model.pkl"
        if path.exists():
            models[name] = joblib.load(path)
            print(f"  [OK] {name} cargado")
        else:
            print(f"  [FALTA] {name} ({path})")
    return models


def evaluate(models, X_test, y_test):
    print("\n[3/5] Evaluando modelos...")
    results = {}
    for name, model in models.items():
        t0 = time.time()
        y_pred = np.maximum(model.predict(X_test), 0)
        pred_time = time.time() - t0

        mae = float(mean_absolute_error(y_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2 = float(r2_score(y_test, y_pred))
        mape = float(np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 1))) * 100)

        results[name] = {
            "modelo": name.upper(),
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "r2": round(r2, 4),
            "mape": round(mape, 4),
            "pred_time_seconds": round(pred_time, 4),
            "y_pred": y_pred,
        }

        print(f"  {name.upper()}:")
        print(f"    MAE:  {mae:.4f}")
        print(f"    RMSE: {rmse:.4f}")
        print(f"    R2:   {r2:.4f}")
        print(f"    MAPE: {mape:.4f}%")
        print(f"    Tiempo prediccion: {pred_time:.4f}s")

    return results


def create_comparison_report(results):
    print("\n[4/5] Generando reporte de comparacion...")

    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("REPORTE DE COMPARACION: XGBOOST vs LIGHTGBM")
    report_lines.append("=" * 70)
    report_lines.append("")

    header = f"{'Metrica':<20} {'XGBOOST':>15} {'LIGHTGBM':>15} {'Ganador':>15}"
    report_lines.append(header)
    report_lines.append("-" * 70)

    metrics_list = ["mae", "rmse", "r2", "mape"]
    xgb_res = results.get("xgboost", {})
    lgb_res = results.get("lightgbm", {})

    for m in metrics_list:
        xgb_val = xgb_res.get(m, 0)
        lgb_val = lgb_res.get(m, 0)

        if m == "r2":
            winner = "XGBoost" if xgb_val > lgb_val else "LightGBM"
        else:
            winner = "XGBoost" if xgb_val < lgb_val else "LightGBM"

        line = f"{m.upper():<20} {xgb_val:>15.4f} {lgb_val:>15.4f} {winner:>15}"
        report_lines.append(line)

    report_lines.append("-" * 70)
    report_lines.append("")

    xgb_wins = sum(
        1 for m in metrics_list
        if (xgb_res.get(m, 0) < lgb_res.get(m, 0) if m != "r2" else xgb_res.get(m, 0) > lgb_res.get(m, 0))
    )
    lgb_wins = len(metrics_list) - xgb_wins
    overall = "XGBoost" if xgb_wins > lgb_wins else "LightGBM"
    report_lines.append(f"Ganador general: {overall}")
    report_lines.append(f"XGBoost gana en {xgb_wins}/{len(metrics_list)} metricas")
    report_lines.append(f"LightGBM gana en {lgb_wins}/{len(metrics_list)} metricas")
    report_lines.append("")

    for name, res in results.items():
        report_lines.append(f"{name.upper()}:")
        report_lines.append(f"  Tiempo de prediccion: {res.get('pred_time_seconds', 0):.4f}s")

    report = "\n".join(report_lines)
    report_path = METRICS_DIR / "reporte_metricas.txt"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"  Reporte guardado: {report_path}")

    return report


def create_charts(results, y_test):
    print("\n[5/5] Generando graficas...")
    if not HAS_MATPLOTLIB:
        print("  [SKIP] matplotlib/seaborn no instalado. Saltando graficas.")
        return

    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    # Grafica 1: Comparacion de metricas (barras)
    fig, ax = plt.subplots(figsize=(10, 6))
    metric_names = ["MAE", "RMSE", "MAPE"]
    xgb_vals = [results["xgboost"]["mae"], results["xgboost"]["rmse"], results["xgboost"]["mape"]]
    lgb_vals = [results["lightgbm"]["mae"], results["lightgbm"]["rmse"], results["lightgbm"]["mape"]]

    x = np.arange(len(metric_names))
    width = 0.35
    ax.bar(x - width/2, xgb_vals, width, label="XGBoost", color="#3b82f6")
    ax.bar(x + width/2, lgb_vals, width, label="LightGBM", color="#10b981")
    ax.set_ylabel("Valor")
    ax.set_title("Comparacion de Metricas: XGBoost vs LightGBM")
    ax.set_xticks(x)
    ax.set_xticklabels(metric_names)
    ax.legend()
    plt.tight_layout()
    plt.savefig(METRICS_DIR / "comparacion_metricas.png", dpi=150)
    plt.close()
    print("  [OK] comparacion_metricas.png")

    # Grafica 2: Scatter Actual vs Predicho
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for i, (name, res) in enumerate(results.items()):
        ax = axes[i]
        y_pred = res["y_pred"]
        sample_idx = np.random.choice(len(y_test), min(5000, len(y_test)), replace=False)
        ax.scatter(y_test.values[sample_idx], y_pred[sample_idx], alpha=0.3, s=10)
        max_val = max(y_test.max(), y_pred.max())
        ax.plot([0, max_val], [0, max_val], "r--", linewidth=2, label="Ideal")
        ax.set_xlabel("Valor Real")
        ax.set_ylabel("Prediccion")
        ax.set_title(f"Actual vs Predicho - {res['modelo']}")
        ax.legend()
    plt.tight_layout()
    plt.savefig(METRICS_DIR / "actual_vs_predicho.png", dpi=150)
    plt.close()
    print("  [OK] actual_vs_predicho.png")

    # Grafica 3: Feature Importance
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    for i, (name, model) in enumerate(results.items()):
        ax = axes[i]
        importances = model.get("feature_importances_", None) if isinstance(model, dict) else None
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif isinstance(model, dict) and "y_pred" in model:
            importances = None

        if importances is None:
            ax.text(0.5, 0.5, "Feature importance\nno disponible", ha="center", va="center")
            ax.set_title(name.upper())
            continue

        feat_imp = pd.Series(importances, index=FEATURE_COLS).sort_values(ascending=True).tail(15)
        feat_imp.plot(kind="barh", ax=ax, color="#3b82f6" if name == "xgboost" else "#10b981")
        ax.set_title(f"Top 15 Features - {name.upper()}")
        ax.set_xlabel("Importancia")
    plt.tight_layout()
    plt.savefig(METRICS_DIR / "feature_importance.png", dpi=150)
    plt.close()
    print("  [OK] feature_importance.png")

    # Grafica 4: Distribucion de errores
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for i, (name, res) in enumerate(results.items()):
        ax = axes[i]
        errors = y_test.values - res["y_pred"]
        ax.hist(errors, bins=100, color="#3b82f6" if name == "xgboost" else "#10b981", alpha=0.7, edgecolor="white")
        ax.axvline(x=0, color="red", linestyle="--", linewidth=2)
        ax.set_title(f"Distribucion de Errores - {res['modelo']}")
        ax.set_xlabel("Error (Real - Predicho)")
        ax.set_ylabel("Frecuencia")
    plt.tight_layout()
    plt.savefig(METRICS_DIR / "distribucion_errores.png", dpi=150)
    plt.close()
    print("  [OK] distribucion_errores.png")


def main():
    print("=" * 60)
    print("EVALUAR Y COMPARAR MODELOS")
    print("=" * 60)

    X_test, y_test, X_train, y_train = load_data_and_split()
    models = load_models()

    if not models:
        print("\n[ERROR] No hay modelos entrenados. Ejecuta primero 05 y 06.")
        return

    results = evaluate(models, X_test, y_test)

    # Guardar comparativa JSON (sin y_pred)
    comp = {name: {k: v for k, v in res.items() if k != "y_pred"} for name, res in results.items()}
    comp_path = METRICS_DIR / "comparativa_modelos.json"
    with open(comp_path, "w") as f:
        json.dump(comp, f, indent=2)
    print(f"\n  Comparativa JSON: {comp_path}")

    report = create_comparison_report(results)
    print(f"\n{report}")

    create_charts(results, y_test)

    print("\n[OK] Evaluacion completada!")


if __name__ == "__main__":
    main()
