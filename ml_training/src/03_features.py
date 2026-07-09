"""
Script 03: Feature engineering para dataset M5
Entrada: data/processed/m5_largo.csv
Salida: data/processed/dataset_entrenamiento.csv
Features: 19 variables compatibles con backend ml_service.py
"""
import pandas as pd
import numpy as np
import yaml
import time
from pathlib import Path
from datetime import datetime, timedelta

DIRECTORIO_BASE = Path(__file__).resolve().parent.parent
DIRECTORIO_PROCESADO = DIRECTORIO_BASE / "data" / "processed"

with open(DIRECTORIO_BASE / "config.yaml", "r") as f:
    config = yaml.safe_load(f)


def calcular_domingo_pascua(anio: int) -> datetime:
    a = anio % 19
    b = anio // 100
    c = anio % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(anio, mes, dia)


def obtener_festivos_ecuador(anio: int) -> set:
    pascua = calcular_domingo_pascua(anio)
    fijos = [
        f"{anio}-01-01", f"{anio}-05-01", f"{anio}-05-24",
        f"{anio}-08-10", f"{anio}-10-09", f"{anio}-11-02",
        f"{anio}-11-03", f"{anio}-12-25",
    ]
    carnaval_lunes = pascua - timedelta(days=48)
    carnaval_martes = pascua - timedelta(days=47)
    viernes_santo = pascua - timedelta(days=2)
    variables = [
        carnaval_lunes.strftime("%Y-%m-%d"),
        carnaval_martes.strftime("%Y-%m-%d"),
        viernes_santo.strftime("%Y-%m-%d"),
    ]
    return set(fijos + variables)


COLUMNAS_FEATURES = config["features"]


def cargar_datos():
    print("[1/5] Cargando m5_largo.csv...")
    t0 = time.time()
    df = pd.read_csv(DIRECTORIO_PROCESADO / "m5_largo.csv", parse_dates=["date"])
    print(f"  Filas: {df.shape[0]:,} | Columnas: {df.shape[1]}")
    print(f"  Tiempo: {time.time() - t0:.1f}s")
    return df


def construir_features_calendario(df):
    print("\n[2/5] Construyendo features de calendario...")
    df["dia_semana"] = df["date"].dt.dayofweek
    df["mes"] = df["date"].dt.month
    df["fin_de_mes"] = df["date"].dt.is_month_end.astype(np.int8)

    todos_festivos = set()
    for y in range(df["date"].dt.year.min(), df["date"].dt.year.max() + 1):
        todos_festivos.update(obtener_festivos_ecuador(y))
    df["es_festivo"] = df["date"].dt.strftime("%Y-%m-%d").isin(todos_festivos).astype(np.int8)

    df["mes_seno"] = np.sin(2 * np.pi * df["mes"] / 12).astype(np.float32)
    df["dia_semana_seno"] = np.sin(2 * np.pi * df["dia_semana"] / 7).astype(np.float32)

    print("  OK: dia_semana, mes, fin_de_mes, es_festivo, mes_seno, dia_semana_seno")
    return df


def construir_features_rezagos(df):
    print("\n[3/5] Construyendo features de rezago y media movil...")
    t0 = time.time()

    rezagos = [1, 7, 14, 28]
    ventanas = [7, 14, 28]

    df = df.sort_values(["id", "date"]).reset_index(drop=True)
    grupo = df.groupby("id")["y"]

    for rezago in rezagos:
        df[f"rezago_{rezago}"] = grupo.shift(rezago).astype(np.float32)

    for ventana in ventanas:
        df[f"media_movil_{ventana}"] = grupo.shift(1).rolling(ventana, min_periods=1).mean().astype(np.float32)
        df[f"desviacion_estandar_{ventana}"] = grupo.shift(1).rolling(ventana, min_periods=1).std().astype(np.float32)

    df["maximo_movil_28"] = grupo.shift(1).rolling(28, min_periods=1).max().astype(np.float32)
    df["minimo_movil_28"] = grupo.shift(1).rolling(28, min_periods=1).min().astype(np.float32)

    df["cambio_precio_1"] = df.groupby("id")["price"].pct_change().astype(np.float32)

    print(f"  Rezagos: {rezagos}")
    print(f"  Ventanas: {ventanas} + max/min_28")
    print(f"  Tiempo: {time.time() - t0:.1f}s")
    return df


def construir_dataset_entrenamiento(df):
    print("\n[4/5] Construyendo dataset de entrenamiento para ML...")
    t0 = time.time()

    # Renombrar columnas de ingles a espanol
    df["precio"] = df["price"]

    columnas_salida = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id", "date", "y"] + COLUMNAS_FEATURES

    df_ml = df[columnas_salida]
    df_ml = df_ml.dropna(subset=["rezago_28", "media_movil_28"])

    print(f"  Dataset ML: {df_ml.shape[0]:,} filas x {df_ml.shape[1]} columnas")
    print(f"  Features: {len(COLUMNAS_FEATURES)}")
    print(f"  Tiempo: {time.time() - t0:.1f}s")
    return df_ml


def guardar_dataset_por_chunks(df_ml, ruta_salida):
    print("\n[5/5] Guardando dataset_entrenamiento.csv...")
    t0 = time.time()
    tamano_chunk = 200_000
    total_filas = len(df_ml)

    for i in range(0, total_filas, tamano_chunk):
        chunk = df_ml.iloc[i:i + tamano_chunk]
        if i == 0:
            chunk.to_csv(ruta_salida, index=False, mode="w")
        else:
            chunk.to_csv(ruta_salida, index=False, mode="a", header=False)

    tamano_mb = ruta_salida.stat().st_size / (1024 * 1024)
    print(f"  Tamano: {tamano_mb:.1f} MB")
    print(f"  Tiempo: {time.time() - t0:.1f}s")


def main():
    print("=" * 60)
    print("FEATURE ENGINEERING - 19 FEATURES BACKEND")
    print("=" * 60)

    df = cargar_datos()
    df = construir_features_calendario(df)
    df = construir_features_rezagos(df)
    df_ml = construir_dataset_entrenamiento(df)

    del df

    ruta_ml = DIRECTORIO_PROCESADO / "dataset_entrenamiento.csv"
    guardar_dataset_por_chunks(df_ml, ruta_ml)

    print(f"\n[OK] Feature engineering completado!")


if __name__ == "__main__":
    main()
