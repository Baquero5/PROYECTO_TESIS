"""
Script 01: Copiar datos M5 desde carpeta del usuario
Entrada: Carpeta de descargas del usuario
Salida: data/raw/*.csv
"""
import shutil
from pathlib import Path

DIRECTORIO_BASE = Path(__file__).resolve().parent.parent
DIRECTORIO_RAW = DIRECTORIO_BASE / "data" / "raw"

ARCHIVOS_REQUERIDOS = [
    "sales_train_validation.csv",
    "sell_prices.csv",
    "calendar.csv",
]


def main():
    print("=" * 60)
    print("COPIAR DATOS M5 - CARPETA DEL USUARIO")
    print("=" * 60)

    with open(DIRECTORIO_BASE / "config.yaml", "r") as f:
        import yaml
        config = yaml.safe_load(f)

    directorio_origen = Path(config["dataset"]["source_path"])
    print(f"\nOrigen: {directorio_origen}")
    print(f"Destino: {DIRECTORIO_RAW}")

    if not directorio_origen.exists():
        print(f"\n[ERROR] Carpeta no encontrada: {directorio_origen}")
        return

    DIRECTORIO_RAW.mkdir(parents=True, exist_ok=True)

    for archivo in ARCHIVOS_REQUERIDOS:
        origen = directorio_origen / archivo
        destino = DIRECTORIO_RAW / archivo

        if not origen.exists():
            print(f"  [FALTA] {archivo} en origen")
            continue

        if destino.exists():
            tamano_origen = origen.stat().st_size / (1024 * 1024)
            tamano_destino = destino.stat().st_size / (1024 * 1024)
            if abs(tamano_origen - tamano_destino) < 1:
                print(f"  [SKIP] {archivo} ya existe ({tamano_destino:.1f} MB)")
                continue

        shutil.copy2(origen, destino)
        tamano = destino.stat().st_size / (1024 * 1024)
        print(f"  [OK] {archivo} ({tamano:.1f} MB)")

    print("\nVerificando archivos...")
    todos_ok = True
    for archivo in ARCHIVOS_REQUERIDOS:
        ruta = DIRECTORIO_RAW / archivo
        if ruta.exists():
            tamano = ruta.stat().st_size / (1024 * 1024)
            print(f"  [OK] {archivo} ({tamano:.1f} MB)")
        else:
            print(f"  [FALTA] {archivo}")
            todos_ok = False

    if todos_ok:
        print("\n[OK] Datos M5 listos para procesar!")
    else:
        print("\n[ERROR] Faltan archivos. Verifica la carpeta de origen.")


if __name__ == "__main__":
    main()
