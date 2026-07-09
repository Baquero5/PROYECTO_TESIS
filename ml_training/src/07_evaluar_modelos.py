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
    TIENE_MATPLOTLIB = True
except ImportError:
    TIENE_MATPLOTLIB = False

DIRECTORIO_BASE = Path(__file__).resolve().parent.parent
DIRECTORIO_PROCESADO = DIRECTORIO_BASE / "data" / "processed"
DIRECTORIO_MODELOS = DIRECTORIO_BASE / "models"
DIRECTORIO_METRICAS = DIRECTORIO_BASE / "metrics"

with open(DIRECTORIO_BASE / "config.yaml", "r") as f:
    import yaml
    config = yaml.safe_load(f)

COLUMNAS_FEATURES = config["features"]


def cargar_datos_y_dividir():
    print("[1/5] Cargando dataset...")
    df = pd.read_csv(DIRECTORIO_PROCESADO / "dataset_entrenamiento.csv")
    X = df[COLUMNAS_FEATURES].fillna(0)
    y = df["y"].fillna(0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"  Test: {X_test.shape[0]:,} muestras")
    return X_test, y_test, X_train, y_train


def cargar_modelos():
    print("\n[2/5] Cargando modelos entrenados...")
    modelos = {}
    for nombre in ["xgboost", "lightgbm"]:
        ruta = DIRECTORIO_MODELOS / f"{nombre}_model.pkl"
        if ruta.exists():
            modelos[nombre] = joblib.load(ruta)
            print(f"  [OK] {nombre} cargado")
        else:
            print(f"  [FALTA] {nombre} ({ruta})")
    return modelos


def evaluar(modelos, X_test, y_test):
    print("\n[3/5] Evaluando modelos...")
    resultados = {}
    for nombre, modelo in modelos.items():
        t0 = time.time()
        y_pred = np.maximum(modelo.predict(X_test), 0)
        tiempo_prediccion = time.time() - t0

        mae = float(mean_absolute_error(y_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2 = float(r2_score(y_test, y_pred))
        mape = float(np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 1))) * 100)

        resultados[nombre] = {
            "modelo": nombre.upper(),
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "r2": round(r2, 4),
            "mape": round(mape, 4),
            "pred_time_seconds": round(tiempo_prediccion, 4),
            "y_pred": y_pred,
        }

        print(f"  {nombre.upper()}:")
        print(f"    MAE:  {mae:.4f}")
        print(f"    RMSE: {rmse:.4f}")
        print(f"    R2:   {r2:.4f}")
        print(f"    MAPE: {mape:.4f}%")
        print(f"    Tiempo prediccion: {tiempo_prediccion:.4f}s")

    return resultados


def crear_reporte_comparacion(resultados):
    print("\n[4/5] Generando reporte de comparacion...")

    lineas_reporte = []
    lineas_reporte.append("=" * 70)
    lineas_reporte.append("REPORTE DE COMPARACION: XGBOOST vs LIGHTGBM")
    lineas_reporte.append("=" * 70)
    lineas_reporte.append("")

    encabezado = f"{'Metrica':<20} {'XGBOOST':>15} {'LIGHTGBM':>15} {'Ganador':>15}"
    lineas_reporte.append(encabezado)
    lineas_reporte.append("-" * 70)

    metricas_lista = ["mae", "rmse", "r2", "mape"]
    res_xgb = resultados.get("xgboost", {})
    res_lgb = resultados.get("lightgbm", {})

    for m in metricas_lista:
        val_xgb = res_xgb.get(m, 0)
        val_lgb = res_lgb.get(m, 0)

        if m == "r2":
            ganador = "XGBoost" if val_xgb > val_lgb else "LightGBM"
        else:
            ganador = "XGBoost" if val_xgb < val_lgb else "LightGBM"

        linea = f"{m.upper():<20} {val_xgb:>15.4f} {val_lgb:>15.4f} {ganador:>15}"
        lineas_reporte.append(linea)

    lineas_reporte.append("-" * 70)
    lineas_reporte.append("")

    victorias_xgb = sum(
        1 for m in metricas_lista
        if (res_xgb.get(m, 0) < res_lgb.get(m, 0) if m != "r2" else res_xgb.get(m, 0) > res_lgb.get(m, 0))
    )
    victorias_lgb = len(metricas_lista) - victorias_xgb
    ganador_general = "XGBoost" if victorias_xgb > victorias_lgb else "LightGBM"
    lineas_reporte.append(f"Ganador general: {ganador_general}")
    lineas_reporte.append(f"XGBoost gana en {victorias_xgb}/{len(metricas_lista)} metricas")
    lineas_reporte.append(f"LightGBM gana en {victorias_lgb}/{len(metricas_lista)} metricas")
    lineas_reporte.append("")

    for nombre, res in resultados.items():
        lineas_reporte.append(f"{nombre.upper()}:")
        lineas_reporte.append(f"  Tiempo de prediccion: {res.get('pred_time_seconds', 0):.4f}s")

    reporte = "\n".join(lineas_reporte)
    ruta_reporte = DIRECTORIO_METRICAS / "reporte_metricas.txt"
    with open(ruta_reporte, "w") as f:
        f.write(reporte)
    print(f"  Reporte guardado: {ruta_reporte}")

    return reporte


def crear_graficas(resultados, y_test):
    print("\n[5/5] Generando graficas...")
    if not TIENE_MATPLOTLIB:
        print("  [SKIP] matplotlib/seaborn no instalado. Saltando graficas.")
        return

    DIRECTORIO_METRICAS.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    nombres_metricas = ["MAE", "RMSE", "MAPE"]
    valores_xgb = [resultados["xgboost"]["mae"], resultados["xgboost"]["rmse"], resultados["xgboost"]["mape"]]
    valores_lgb = [resultados["lightgbm"]["mae"], resultados["lightgbm"]["rmse"], resultados["lightgbm"]["mape"]]

    x = np.arange(len(nombres_metricas))
    ancho = 0.35
    ax.bar(x - ancho/2, valores_xgb, ancho, label="XGBoost", color="#3b82f6")
    ax.bar(x + ancho/2, valores_lgb, ancho, label="LightGBM", color="#10b981")
    ax.set_ylabel("Valor")
    ax.set_title("Comparacion de Metricas: XGBoost vs LightGBM")
    ax.set_xticks(x)
    ax.set_xticklabels(nombres_metricas)
    ax.legend()
    plt.tight_layout()
    plt.savefig(DIRECTORIO_METRICAS / "comparacion_metricas.png", dpi=150)
    plt.close()
    print("  [OK] comparacion_metricas.png")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for i, (nombre, res) in enumerate(resultados.items()):
        ax = axes[i]
        y_pred = res["y_pred"]
        indice_muestra = np.random.choice(len(y_test), min(5000, len(y_test)), replace=False)
        ax.scatter(y_test.values[indice_muestra], y_pred[indice_muestra], alpha=0.3, s=10)
        valor_max = max(y_test.max(), y_pred.max())
        ax.plot([0, valor_max], [0, valor_max], "r--", linewidth=2, label="Ideal")
        ax.set_xlabel("Valor Real")
        ax.set_ylabel("Prediccion")
        ax.set_title(f"Actual vs Predicho - {res['modelo']}")
        ax.legend()
    plt.tight_layout()
    plt.savefig(DIRECTORIO_METRICAS / "actual_vs_predicho.png", dpi=150)
    plt.close()
    print("  [OK] actual_vs_predicho.png")

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    for i, (nombre, modelo) in enumerate(resultados.items()):
        ax = axes[i]
        if hasattr(modelo, "feature_importances_"):
            importancias = modelo.feature_importances_
        else:
            ax.text(0.5, 0.5, "Feature importance\nno disponible", ha="center", va="center")
            ax.set_title(nombre.upper())
            continue

        imp_features = pd.Series(importancias, index=COLUMNAS_FEATURES).sort_values(ascending=True).tail(15)
        imp_features.plot(kind="barh", ax=ax, color="#3b82f6" if nombre == "xgboost" else "#10b981")
        ax.set_title(f"Top 15 Features - {nombre.upper()}")
        ax.set_xlabel("Importancia")
    plt.tight_layout()
    plt.savefig(DIRECTORIO_METRICAS / "feature_importance.png", dpi=150)
    plt.close()
    print("  [OK] feature_importance.png")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for i, (nombre, res) in enumerate(resultados.items()):
        ax = axes[i]
        errores = y_test.values - res["y_pred"]
        ax.hist(errores, bins=100, color="#3b82f6" if nombre == "xgboost" else "#10b981", alpha=0.7, edgecolor="white")
        ax.axvline(x=0, color="red", linestyle="--", linewidth=2)
        ax.set_title(f"Distribucion de Errores - {res['modelo']}")
        ax.set_xlabel("Error (Real - Predicho)")
        ax.set_ylabel("Frecuencia")
    plt.tight_layout()
    plt.savefig(DIRECTORIO_METRICAS / "distribucion_errores.png", dpi=150)
    plt.close()
    print("  [OK] distribucion_errores.png")


def main():
    print("=" * 60)
    print("EVALUAR Y COMPARAR MODELOS")
    print("=" * 60)

    X_test, y_test, X_train, y_train = cargar_datos_y_dividir()
    modelos = cargar_modelos()

    if not modelos:
        print("\n[ERROR] No hay modelos entrenados. Ejecuta primero 05 y 06.")
        return

    resultados = evaluar(modelos, X_test, y_test)

    comp = {nombre: {k: v for k, v in res.items() if k != "y_pred"} for nombre, res in resultados.items()}
    DIRECTORIO_METRICAS.mkdir(parents=True, exist_ok=True)
    ruta_comp = DIRECTORIO_METRICAS / "comparativa_modelos.json"
    with open(ruta_comp, "w") as f:
        json.dump(comp, f, indent=2)
    print(f"\n  Comparativa JSON: {ruta_comp}")

    reporte = crear_reporte_comparacion(resultados)
    print(f"\n{reporte}")

    crear_graficas(resultados, y_test)

    print("\n[OK] Evaluacion completada!")


if __name__ == "__main__":
    main()
