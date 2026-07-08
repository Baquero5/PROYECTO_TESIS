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

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROC_DIR = BASE_DIR / "data" / "processed"

with open(BASE_DIR / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

TIENDAS = config["dataset"]["tiendas"]
NUM_PRODUCTOS = config["dataset"]["num_productos"]
SUBCATS = config["dataset"]["subcategorias"]

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


def select_balanced_products(sales):
    print(f"\n[2/6] Seleccionando {NUM_PRODUCTOS} productos balanceados...")

    foods = sales[sales["cat_id"] == "FOODS"].copy()
    foods_5stores = foods[foods["store_id"].isin(TIENDAS)].copy()

    value_cols = [c for c in foods_5stores.columns if c.startswith("d_")]
    foods_5stores["total_demand"] = foods_5stores[value_cols].sum(axis=1)

    item_stats = foods_5stores.groupby(["item_id", "dept_id"]).agg(
        total_demand=("total_demand", "sum"),
        num_stores=("store_id", "nunique")
    ).reset_index()

    selected_items = []
    for dept, info in SUBCATS.items():
        dept_items = item_stats[item_stats["dept_id"] == dept]
        n_per_subcat = NUM_PRODUCTOS // len(SUBCATS)
        if dept == "FOODS_3":
            n_per_subcat = NUM_PRODUCTOS - n_per_subcat * (len(SUBCATS) - 1)
        top = dept_items.nlargest(n_per_subcat, "total_demand")
        selected_items.append(top)
        print(f"  {info['nombre']}: {len(top)} productos")

    selected = pd.concat(selected_items)
    print(f"\n  Total productos seleccionados: {len(selected)}")

    sales_filtered = foods_5stores[foods_5stores["item_id"].isin(selected["item_id"])].copy()
    sales_filtered.drop(columns=["total_demand"], inplace=True, errors="ignore")

    print(f"  Registros (item x store): {sales_filtered.shape[0]:,}")
    return sales_filtered


def melt_to_long(sales_filtered):
    print("\n[3/6] Convirtiendo de formato ancho a largo (MELT)...")
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
    print("\n[4/6] Mergeando con calendar y precios...")

    calendar["date"] = pd.to_datetime(calendar["date"])
    df = df.merge(calendar, on="d", how="left")
    print(f"  Despues de merge con calendar: {df.shape[0]:,} filas")

    df = df.merge(prices, on=["store_id", "item_id", "wm_yr_wk"], how="left")
    print(f"  Despues de merge con precios: {df.shape[0]:,} filas")

    return df


def sort_and_clean(df):
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


def save_dataset(df):
    print("\n[6/6] Guardando m5_largo.csv...")
    t0 = time.time()

    output_path = PROC_DIR / "m5_largo.csv"
    chunk_size = 500_000
    total_rows = len(df)

    for i in range(0, total_rows, chunk_size):
        chunk = df.iloc[i:i + chunk_size]
        if i == 0:
            chunk.to_csv(output_path, index=False, mode="w")
        else:
            chunk.to_csv(output_path, index=False, mode="a", header=False)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  Tamanio: {size_mb:.1f} MB")
    print(f"  Tiempo: {time.time() - t0:.1f}s")


def main():
    print("=" * 60)
    print("TRANSFORMAR DATASET M5 - ANCHO A LARGO")
    print(f"Config: {NUM_PRODUCTOS} productos, {len(TIENDAS)} tiendas, {len(SUBCATS)} subcategorias")
    print("=" * 60)

    PROC_DIR.mkdir(parents=True, exist_ok=True)

    sales, calendar, prices = load_raw_data()
    sales_filtered = select_balanced_products(sales)
    df = melt_to_long(sales_filtered)
    df = merge_calendar_and_prices(df, calendar, prices)
    df = sort_and_clean(df)
    save_dataset(df)

    print(f"\n[OK] Transformacion completada!")


if __name__ == "__main__":
    main()
