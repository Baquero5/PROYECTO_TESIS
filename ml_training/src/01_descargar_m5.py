"""
Script 01: Descargar dataset M5 de Kaggle
Salida: data/raw/sales_train_validation.csv, sell_prices.csv, calendar.csv
"""
import os
import sys
import yaml
import zipfile
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

M5_URLS = {
    "m5-forecasting-accuracy.zip": "https://www.kaggle.com/api/v1/competitions/download/m5-forecasting-accuracy",
    "sales_train_validation.csv.zip": None,
    "sell_prices.csv.zip": None,
    "calendar.csv.zip": None,
}

KAGGLE_KERNEL_REF = "m5-forecasting-accuracy"


def download_via_kagglehub():
    """Descargar usando kagglehub si esta disponible."""
    try:
        import kagglehub
        print("[INFO] Descargando dataset M5 via kagglehub...")
        # kagglehub.competition_download() sin keyword arguments
        path = kagglehub.competition_download("m5-forecasting-accuracy")
        print(f"[OK] Dataset descargado en: {path}")
        return path
    except ImportError:
        print("[WARN] kagglehub no esta instalado. Intentando descarga manual...")
        return None
    except Exception as e:
        print(f"[ERROR] kagglehub fallo: {e}")
        return None


def download_via_kaggle_cli():
    """Descargar usando el CLI de kaggle."""
    try:
        import subprocess
        print("[INFO] Intentando descargar via kaggle CLI...")
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["kaggle", "competitions", "download", "-c", "m5-forecasting-accuracy",
             "-p", str(RAW_DIR)],
            check=True
        )
        print("[OK] Descarga via CLI completada")
        return RAW_DIR
    except FileNotFoundError:
        print("[WARN] kaggle CLI no encontrado")
        return None
    except Exception as e:
        print(f"[ERROR] kaggle CLI fallo: {e}")
        return None


def extract_if_needed(source_dir):
    """Extraer archivos ZIP si existen en source_dir."""
    import glob
    zips = glob.glob(str(source_dir / "*.zip"))
    if zips:
        for z in zips:
            print(f"[INFO] Extrayendo {os.path.basename(z)}...")
            with zipfile.ZipFile(z, 'r') as zip_ref:
                zip_ref.extractall(source_dir)
            print(f"[OK] Extraido: {os.path.basename(z)}")
    return source_dir


def move_files_to_raw(source_dir):
    """Mover archivos CSV a data/raw/."""
    import glob
    csv_files = glob.glob(str(source_dir / "*.csv"))
    if not csv_files:
        csv_files = glob.glob(str(source_dir / "**/*.csv"), recursive=True)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for csv in csv_files:
        filename = os.path.basename(csv)
        dest = RAW_DIR / filename
        if not dest.exists():
            import shutil
            shutil.copy2(csv, dest)
            print(f"[OK] Movido: {filename}")
        else:
            print(f"[SKIP] Ya existe: {filename}")


def verify_files():
    """Verificar que los archivos necesarios existen."""
    required = ["sales_train_validation.csv", "sell_prices.csv", "calendar.csv"]
    missing = []
    for f in required:
        if (RAW_DIR / f).exists():
            size = (RAW_DIR / f).stat().st_size / (1024 * 1024)
            print(f"  [OK] {f} ({size:.1f} MB)")
        else:
            missing.append(f)
            print(f"  [FALTA] {f}")
    return missing


def main():
    print("=" * 60)
    print("DESCARGAR DATASET M5 - WALMART SALES FORECASTING")
    print("=" * 60)
    print()

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    required_files = ["sales_train_validation.csv", "sell_prices.csv", "calendar.csv"]
    all_exist = all((RAW_DIR / f).exists() for f in required_files)

    if all_exist:
        print("[INFO] Todos los archivos ya existen en data/raw/")
        verify_files()
        return

    print("[INFO] Intentando descargar dataset M5...")
    print()

    # Intentar kagglehub primero
    source = download_via_kagglehub()
    if source:
        extract_if_needed(Path(source))
        move_files_to_raw(Path(source))

    # Si no funciono, intentar CLI
    if not source or not all((RAW_DIR / f).exists() for f in required_files):
        source = download_via_kaggle_cli()
        if source:
            extract_if_needed(Path(source))
            move_files_to_raw(Path(source))

    print()
    print("[INFO] Verificando archivos...")
    missing = verify_files()

    if missing:
        print()
        print("[ERROR] Faltan archivos. Descarga manual:")
        print("  1. Ve a: https://www.kaggle.com/competitions/m5-forecasting-accuracy/data")
        print("  2. Descarga: sales_train_validation.csv, sell_prices.csv, calendar.csv")
        print(f"  3. Colocalos en: {RAW_DIR}")
        sys.exit(1)

    print()
    print("[OK] Dataset M5 listo para procesar!")


if __name__ == "__main__":
    main()
