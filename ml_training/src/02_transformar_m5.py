"""
Script 02: Transformar dataset M5 de formato ancho a largo
Entrada: data/raw/*.csv
Salida: data/processed/m5_largo.csv
"""
import pandas as pd
import numpy as np
import yaml
from pathlib import Path
import time

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROC_DIR = BASE_DIR / "data" / "processed"

with open(BASE_DIR / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

TIENDAS = config["dataset"]["tiendas"]
NUM_PRODUCTOS = config["dataset"]["num_productos"]

ID_COLS = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]


def load_raw_data():
    print("[1/6] Cargando archivos CSV...")
    t0 = time.time()

    sales = pd.read_csv(RAW_DIR / "sales_train_validation.csv")
    print(f"  - sales_train_validation.csv: {sales.shape[0]:,} filas x {sales.shape[1]} columnas")

    calendar = pd.read_csv(RAW_DIR / "calendar.csv")
    print(f"  - calendar.csv: {calendar.shape[0]:,} filas")

    prices = pd.read_csv(RAW_DIR / "sell_prices.csv")
    print(f"  - sell_prices.csv: {prices.shape[0]:,} filas")

    print(f"  Cargado en {time.time() - t0:.1f}s")
    return sales, calendar, prices


def filter_stores_and_products(sales):
    print(f"\n[2/6] Filtrando tiendas {TIENDAS}...")
    sales_filtered = sales[sales["store_id"].isin(TIENDAS)].copy()
    print(f"  Filas despues del filtro de tiendas: {sales_filtered.shape[0]:,}")

    value_cols = [c for c in sales_filtered.columns if c.startswith("d_")]
    sales_filtered["total_demand"] = sales_filtered[value_cols].sum(axis=1)
    top_products = (
        sales_filtered.groupby("item_id")["total_demand"]
        .sum()
        .sort_values(ascending=False)
        .head(NUM_PRODUCTOS)
        .index.tolist()
    )

    print(f"\n[3/6] Seleccionando top {len(top_products)} productos por demanda...")
    sales_filtered = sales_filtered[sales_filtered["item_id"].isin(top_products)].copy()
    print(f"  Filas despues del filtro de productos: {sales_filtered.shape[0]:,}")
    sales_filtered.drop(columns=["total_demand"], inplace=True)

    return sales_filtered


def melt_to_long(sales_filtered):
    print("\n[4/6] Convirtiendo de formato ancho a largo (MELT)...")
    t0 = time.time()

    value_cols = [c for c in sales_filtered.columns if c.startswith("d_")]
    print(f"  Columnas a melt: {len(value_cols)} (d_1 a d_{len(value_cols)})")

    df = sales_filtered.melt(
        id_vars=ID_COLS,
        value_vars=value_cols,
        var_name="d",
        value_name="y"
    )
    df["y"] = df["y"].astype(np.float32)
    print(f"  Resultado: {df.shape[0]:,} filas x {df.shape[1]} columnas")
    print(f"  Tiempo: {time.time() - t0:.1f}s")

    return df


def merge_calendar_and_prices(df, calendar, prices):
    print("\n[5/6] Mergeando con calendar y precios...")

    calendar["date"] = pd.to_datetime(calendar["date"])
    df = df.merge(calendar, on="d", how="left")
    print(f"  Despues de merge con calendar: {df.shape[0]:,} filas")

    df = df.merge(prices, on=["store_id", "item_id", "wm_yr_wk"], how="left")
    print(f"  Despues de merge con precios: {df.shape[0]:,} filas")

    return df


def sort_and_clean(df):
    print("\n[6/6] Ordenando y limpiando...")
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


def main():
    print("=" * 60)
    print("TRANSFORMAR DATASET M5 - ANCHO A LARGO")
    print("=" * 60)

    PROC_DIR.mkdir(parents=True, exist_ok=True)

    sales, calendar, prices = load_raw_data()
    sales_filtered = filter_stores_and_products(sales)
    df = melt_to_long(sales_filtered)
    df = merge_calendar_and_prices(df, calendar, prices)
    df = sort_and_clean(df)

    output_path = PROC_DIR / "m5_largo.csv"
    print(f"\nGuardando en {output_path}...")
    df.to_csv(output_path, index=False)
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Archivo guardado: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
