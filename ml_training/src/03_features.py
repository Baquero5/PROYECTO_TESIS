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

BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data" / "processed"

with open(BASE_DIR / "config.yaml", "r") as f:
    config = yaml.safe_load(f)


def calc_easter_sunday(year: int) -> datetime:
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
    return datetime(year, month, day)


def get_ecuador_holidays(year: int) -> set:
    easter = calc_easter_sunday(year)
    fixed = [
        f"{year}-01-01", f"{year}-05-01", f"{year}-05-24",
        f"{year}-08-10", f"{year}-10-09", f"{year}-11-02",
        f"{year}-11-03", f"{year}-12-25",
    ]
    carnaval_lunes = easter - timedelta(days=48)
    carnaval_martes = easter - timedelta(days=47)
    viernes_santo = easter - timedelta(days=2)
    variable = [
        carnaval_lunes.strftime("%Y-%m-%d"),
        carnaval_martes.strftime("%Y-%m-%d"),
        viernes_santo.strftime("%Y-%m-%d"),
    ]
    return set(fixed + variable)


FEATURE_COLS = config["features"]


def load_data():
    print("[1/5] Cargando m5_largo.csv...")
    t0 = time.time()
    df = pd.read_csv(PROC_DIR / "m5_largo.csv", parse_dates=["date"])
    print(f"  Filas: {df.shape[0]:,} | Columnas: {df.shape[1]}")
    print(f"  Tiempo: {time.time() - t0:.1f}s")
    return df


def build_calendar_features(df):
    print("\n[2/5] Construyendo features de calendario...")
    df["dayofweek"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["is_month_end"] = df["date"].dt.is_month_end.astype(np.int8)

    all_holidays = set()
    for y in range(df["date"].dt.year.min(), df["date"].dt.year.max() + 1):
        all_holidays.update(get_ecuador_holidays(y))
    df["is_holiday"] = df["date"].dt.strftime("%Y-%m-%d").isin(all_holidays).astype(np.int8)

    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12).astype(np.float32)
    df["dayofweek_sin"] = np.sin(2 * np.pi * df["dayofweek"] / 7).astype(np.float32)

    print("  OK: dayofweek, month, is_month_end, is_holiday, month_sin, dayofweek_sin")
    return df


def build_lag_features(df):
    print("\n[3/5] Construyendo features de lag y rolling...")
    t0 = time.time()

    lags = [1, 7, 14, 28]
    rolling_windows = [7, 14, 28]

    df = df.sort_values(["id", "date"]).reset_index(drop=True)
    grp = df.groupby("id")["y"]

    for lag in lags:
        df[f"lag_{lag}"] = grp.shift(lag).astype(np.float32)

    for w in rolling_windows:
        df[f"rolling_mean_{w}"] = grp.shift(1).rolling(w, min_periods=1).mean().astype(np.float32)
        df[f"rolling_std_{w}"] = grp.shift(1).rolling(w, min_periods=1).std().astype(np.float32)

    df["rolling_max_28"] = grp.shift(1).rolling(28, min_periods=1).max().astype(np.float32)
    df["rolling_min_28"] = grp.shift(1).rolling(28, min_periods=1).min().astype(np.float32)

    df["price_change_1"] = df.groupby("id")["price"].pct_change().astype(np.float32)

    print(f"  Lags: {lags}")
    print(f"  Rolling: {rolling_windows} + max/min_28")
    print(f"  Tiempo: {time.time() - t0:.1f}s")
    return df


def build_dataset_entrenamiento(df):
    print("\n[4/5] Construyendo dataset de entrenamiento para ML...")
    t0 = time.time()

    output_cols = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id", "date", "y"] + FEATURE_COLS

    df_ml = df[output_cols]
    df_ml = df_ml.dropna(subset=["lag_28", "rolling_mean_28"])

    print(f"  Dataset ML: {df_ml.shape[0]:,} filas x {df_ml.shape[1]} columnas")
    print(f"  Features: {len(FEATURE_COLS)}")
    print(f"  Tiempo: {time.time() - t0:.1f}s")
    return df_ml


def save_dataset_chunked(df_ml, output_path):
    print("\n[5/5] Guardando dataset_entrenamiento.csv...")
    t0 = time.time()
    chunk_size = 200_000
    total_rows = len(df_ml)

    for i in range(0, total_rows, chunk_size):
        chunk = df_ml.iloc[i:i + chunk_size]
        if i == 0:
            chunk.to_csv(output_path, index=False, mode="w")
        else:
            chunk.to_csv(output_path, index=False, mode="a", header=False)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  Tamanio: {size_mb:.1f} MB")
    print(f"  Tiempo: {time.time() - t0:.1f}s")


def main():
    print("=" * 60)
    print("FEATURE ENGINEERING - 19 FEATURES BACKEND")
    print("=" * 60)

    df = load_data()
    df = build_calendar_features(df)
    df = build_lag_features(df)
    df_ml = build_dataset_entrenamiento(df)

    del df

    output_ml = PROC_DIR / "dataset_entrenamiento.csv"
    save_dataset_chunked(df_ml, output_ml)

    print(f"\n[OK] Feature engineering completado!")


if __name__ == "__main__":
    main()
