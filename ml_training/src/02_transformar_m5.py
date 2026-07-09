"""
Script 02: Transformar dataset M5 de formato ancho a largo
Entrada: data/raw/*.csv
Salida: data/processed/m5_largo.csv
Seleccion: Top 100 productos FOODS, balanceados por subcategoria (33/33/34)
"""
import pandas as pd
import numpy as np
import yaml
import time
from pathlib import Path

DIRECTORIO_BASE = Path(__file__).resolve().parent.parent
DIRECTORIO_RAW = DIRECTORIO_BASE / "data" / "raw"
DIRECTORIO_PROCESADO = DIRECTORIO_BASE / "data" / "processed"

with open(DIRECTORIO_BASE / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

TIENDAS = config["dataset"]["tiendas"]
NUM_PRODUCTOS = config["dataset"]["num_productos"]
SUBCATS = config["dataset"]["subcategorias"]

COLUMNAS_ID = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]


def cargar_datos_crudos():
    print("[1/6] Cargando archivos CSV...")
    t0 = time.time()

    ventas = pd.read_csv(DIRECTORIO_RAW / "sales_train_validation.csv")
    print(f"  - sales_train_validation.csv: {ventas.shape[0]:,} filas x {ventas.shape[1]} columnas")

    calendario = pd.read_csv(DIRECTORIO_RAW / "calendar.csv")
    print(f"  - calendar.csv: {calendario.shape[0]:,} filas")

    precios = pd.read_csv(DIRECTORIO_RAW / "sell_prices.csv")
    print(f"  - sell_prices.csv: {precios.shape[0]:,} filas")

    print(f"  Cargado en {time.time() - t0:.1f}s")
    return ventas, calendario, precios


def seleccionar_productos_balanceados(ventas):
    print(f"\n[2/6] Seleccionando {NUM_PRODUCTOS} productos balanceados...")

    alimentos = ventas[ventas["cat_id"] == "FOODS"].copy()
    alimentos_5tiendas = alimentos[alimentos["store_id"].isin(TIENDAS)].copy()

    columnas_val = [c for c in alimentos_5tiendas.columns if c.startswith("d_")]
    alimentos_5tiendas["demanda_total"] = alimentos_5tiendas[columnas_val].sum(axis=1)

    estadisticas_productos = alimentos_5tiendas.groupby(["item_id", "dept_id"]).agg(
        demanda_total=("demanda_total", "sum"),
        num_tiendas=("store_id", "nunique")
    ).reset_index()

    productos_seleccionados = []
    for dept, info in SUBCATS.items():
        productos_dept = estadisticas_productos[estadisticas_productos["dept_id"] == dept]
        n_por_subcat = NUM_PRODUCTOS // len(SUBCATS)
        if dept == "FOODS_3":
            n_por_subcat = NUM_PRODUCTOS - n_por_subcat * (len(SUBCATS) - 1)
        top = productos_dept.nlargest(n_por_subcat, "demanda_total")
        productos_seleccionados.append(top)
        print(f"  {info['nombre']}: {len(top)} productos")

    seleccionados = pd.concat(productos_seleccionados)
    print(f"\n  Total productos seleccionados: {len(seleccionados)}")

    ventas_filtradas = alimentos_5tiendas[alimentos_5tiendas["item_id"].isin(seleccionados["item_id"])].copy()
    ventas_filtradas.drop(columns=["demanda_total"], inplace=True, errors="ignore")

    print(f"  Registros (item x tienda): {ventas_filtradas.shape[0]:,}")
    return ventas_filtradas


def convertir_a_largo(ventas_filtradas):
    print("\n[3/6] Convirtiendo de formato ancho a largo (MELT)...")
    t0 = time.time()

    columnas_val = [c for c in ventas_filtradas.columns if c.startswith("d_")]
    print(f"  Columnas a melt: {len(columnas_val)} (d_1 a d_{len(columnas_val)})")

    df = ventas_filtradas.melt(
        id_vars=COLUMNAS_ID,
        value_vars=columnas_val,
        var_name="d",
        value_name="y"
    )
    df["y"] = df["y"].astype(np.float32)
    print(f"  Resultado: {df.shape[0]:,} filas x {df.shape[1]} columnas")
    print(f"  Tiempo: {time.time() - t0:.1f}s")

    return df


def combinar_calendario_y_precios(df, calendario, precios):
    print("\n[4/6] Mergeando con calendario y precios...")

    calendario["date"] = pd.to_datetime(calendario["date"])
    df = df.merge(calendario, on="d", how="left")
    print(f"  Despues de merge con calendario: {df.shape[0]:,} filas")

    df = df.merge(precios, on=["store_id", "item_id", "wm_yr_wk"], how="left")
    print(f"  Despues de merge con precios: {df.shape[0]:,} filas")

    return df


def ordenar_y_limpiar(df):
    print("\n[5/6] Ordenando y limpiando...")
    df = df.sort_values(["id", "date"]).reset_index(drop=True)

    df["price"] = df["sell_price"].astype(np.float32)
    df["is_available"] = df["price"].notna().astype(np.int8)
    df["price"] = df.groupby("id")["price"].ffill().bfill()
    df["price"] = df["price"].fillna(0.0)

    print(f"  Dataset final: {df.shape[0]:,} filas x {df.shape[1]} columnas")
    print(f"  Rango de fechas: {df['date'].min()} a {df['date'].max()}")
    print(f"  Productos unicos: {df['item_id'].nunique()}")
    print(f"  Tiendas: {df['store_id'].unique().tolist()}")

    return df


def guardar_dataset(df):
    print("\n[6/6] Guardando m5_largo.csv...")
    t0 = time.time()

    DIRECTORIO_PROCESADO.mkdir(parents=True, exist_ok=True)
    ruta_salida = DIRECTORIO_PROCESADO / "m5_largo.csv"
    tamano_chunk = 500_000
    total_filas = len(df)

    for i in range(0, total_filas, tamano_chunk):
        chunk = df.iloc[i:i + tamano_chunk]
        if i == 0:
            chunk.to_csv(ruta_salida, index=False, mode="w")
        else:
            chunk.to_csv(ruta_salida, index=False, mode="a", header=False)

    tamano_mb = ruta_salida.stat().st_size / (1024 * 1024)
    print(f"  Tamano: {tamano_mb:.1f} MB")
    print(f"  Tiempo: {time.time() - t0:.1f}s")


def main():
    print("=" * 60)
    print("TRANSFORMAR DATASET M5 - ANCHO A LARGO")
    print(f"Config: {NUM_PRODUCTOS} productos, {len(TIENDAS)} tiendas, {len(SUBCATS)} subcategorias")
    print("=" * 60)

    DIRECTORIO_PROCESADO.mkdir(parents=True, exist_ok=True)

    ventas, calendario, precios = cargar_datos_crudos()
    ventas_filtradas = seleccionar_productos_balanceados(ventas)
    df = convertir_a_largo(ventas_filtradas)
    df = combinar_calendario_y_precios(df, calendario, precios)
    df = ordenar_y_limpiar(df)
    guardar_dataset(df)

    print(f"\n[OK] Transformacion completada!")


if __name__ == "__main__":
    main()
