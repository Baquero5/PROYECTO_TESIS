"""
Script 01: Copiar datos M5 desde carpeta del usuario
Entrada: Carpeta de descargas del usuario
Salida: data/raw/*.csv
"""
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

REQUIRED_FILES = [
    "sales_train_validation.csv",
    "sell_prices.csv",
    "calendar.csv",
]


def main():
    print("=" * 60)
    print("COPIAR DATOS M5 - CARPETA DEL USUARIO")
    print("=" * 60)

    with open(BASE_DIR / "config.yaml", "r") as f:
        import yaml
        config = yaml.safe_load(f)

    source_dir = Path(config["dataset"]["source_path"])
    print(f"\nOrigen: {source_dir}")
    print(f"Destino: {RAW_DIR}")

    if not source_dir.exists():
        print(f"\n[ERROR] Carpeta no encontrada: {source_dir}")
        return

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for filename in REQUIRED_FILES:
        src = source_dir / filename
        dst = RAW_DIR / filename

        if not src.exists():
            print(f"  [FALTA] {filename} en origen")
            continue

        if dst.exists():
            src_size = src.stat().st_size / (1024 * 1024)
            dst_size = dst.stat().st_size / (1024 * 1024)
            if abs(src_size - dst_size) < 1:
                print(f"  [SKIP] {filename} ya existe ({dst_size:.1f} MB)")
                continue

        shutil.copy2(src, dst)
        size = dst.stat().st_size / (1024 * 1024)
        print(f"  [OK] {filename} ({size:.1f} MB)")

    print("\nVerificando archivos...")
    all_ok = True
    for f in REQUIRED_FILES:
        path = RAW_DIR / f
        if path.exists():
            size = path.stat().st_size / (1024 * 1024)
            print(f"  [OK] {f} ({size:.1f} MB)")
        else:
            print(f"  [FALTA] {f}")
            all_ok = False

    if all_ok:
        print("\n[OK] Datos M5 listos para procesar!")
    else:
        print("\n[ERROR] Faltan archivos. Verifica la carpeta de origen.")


if __name__ == "__main__":
    main()
