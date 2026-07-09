"""
Script 09: Registrar modelos entrenados en la BD
Lee metricas de metrics/*.json y registros en modelo_ia
"""
import pymysql
import json
import os
from pathlib import Path

DIRECTORIO_BASE = Path(__file__).resolve().parent.parent
DIRECTORIO_MODELOS = DIRECTORIO_BASE / "models"
DIRECTORIO_METRICAS = DIRECTORIO_BASE / "metrics"

DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "123456",
    "database": "TESIS",
    "charset": "utf8mb4"
}

DIRECTORIO_MODELOS_BACKEND = Path(__file__).resolve().parent.parent.parent / "backend" / "ml_models"


def obtener_conexion():
    return pymysql.connect(**DB_CONFIG, autocommit=False)


def copiar_modelos_a_backend():
    print("[1/3] Copiando modelos a backend/ml_models/...")
    DIRECTORIO_MODELOS_BACKEND.mkdir(parents=True, exist_ok=True)

    archivos_modelos = [
        "xgboost_model.pkl",
        "lightgbm_model.pkl",
        "ensemble.pkl",
        "ensemble_weights.pkl",
        "feature_columns.pkl",
    ]

    for archivo in archivos_modelos:
        origen = DIRECTORIO_MODELOS / archivo
        destino = DIRECTORIO_MODELOS_BACKEND / archivo
        if origen.exists():
            import shutil
            shutil.copy2(origen, destino)
            tamano = destino.stat().st_size / 1024
            print(f"  [OK] {archivo} ({tamano:.1f} KB)")
        else:
            print(f"  [SKIP] {archivo} no existe")


def registrar_modelos():
    print("\n[2/3] Registrando modelos en BD...")
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("SELECT id_dataset FROM dataset_entrenamiento LIMIT 1")
        resultado = cursor.fetchone()
        if not resultado:
            print("  [ERROR] No hay dataset registrado. Ejecuta primero 04_poblar_bd.py")
            return
        id_dataset = resultado[0]
        print(f"  Dataset ID: {id_dataset}")

        modelos_a_registrar = []

        ruta_xgb = DIRECTORIO_METRICAS / "xgboost_metrics.json"
        if ruta_xgb.exists():
            with open(ruta_xgb) as f:
                m = json.load(f)
            modelos_a_registrar.append({
                "algoritmo": "XGBOOST",
                "version": "1.0",
                "archivo": "xgboost_model.pkl",
                "mae": m["mae"],
                "rmse": m["rmse"],
                "r2": m.get("r2"),
                "mape": m["mape"],
            })

        ruta_lgb = DIRECTORIO_METRICAS / "lightgbm_metrics.json"
        if ruta_lgb.exists():
            with open(ruta_lgb) as f:
                m = json.load(f)
            modelos_a_registrar.append({
                "algoritmo": "LIGHTGBM",
                "version": "1.0",
                "archivo": "lightgbm_model.pkl",
                "mae": m["mae"],
                "rmse": m["rmse"],
                "r2": m.get("r2"),
                "mape": m["mape"],
            })

        ruta_ensemble = DIRECTORIO_METRICAS / "ensemble_metrics.json"
        if ruta_ensemble.exists():
            with open(ruta_ensemble) as f:
                m = json.load(f)
            modelos_a_registrar.append({
                "algoritmo": "ENSEMBLE",
                "version": "1.0",
                "archivo": "ensemble.pkl",
                "mae": m["mae"],
                "rmse": m["rmse"],
                "r2": m.get("r2"),
                "mape": m["mape"],
            })

        for info_modelo in modelos_a_registrar:
            cursor.execute(
                "SELECT id_modelo FROM modelo_ia WHERE algoritmo = %s AND version = %s LIMIT 1",
                (info_modelo["algoritmo"], info_modelo["version"])
            )
            existente = cursor.fetchone()

            if existente:
                cursor.execute(
                    """UPDATE modelo_ia
                       SET archivo_modelo = %s, mae = %s, rmse = %s, r2 = %s, mape = %s, estado = 'INACTIVO'
                       WHERE id_modelo = %s""",
                    (info_modelo["archivo"], info_modelo["mae"], info_modelo["rmse"],
                     info_modelo.get("r2"), info_modelo["mape"], existente[0])
                )
                print(f"  [OK] {info_modelo['algoritmo']} v{info_modelo['version']} actualizado")
            else:
                cursor.execute(
                    """INSERT INTO modelo_ia (id_dataset, algoritmo, version, archivo_modelo, mae, rmse, r2, mape, estado)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (id_dataset, info_modelo["algoritmo"], info_modelo["version"], info_modelo["archivo"],
                     info_modelo["mae"], info_modelo["rmse"], info_modelo.get("r2"), info_modelo["mape"], "INACTIVO")
                )
                print(f"  [OK] {info_modelo['algoritmo']} v{info_modelo['version']} registrado (id={cursor.lastrowid})")

        cursor.execute(
            """UPDATE modelo_ia SET estado = 'ACTIVO'
               WHERE algoritmo = 'LIGHTGBM' AND version = '1.0'
               AND id_modelo = (SELECT id_modelo FROM (SELECT id_modelo FROM modelo_ia WHERE algoritmo = 'LIGHTGBM' AND version = '1.0' LIMIT 1) AS t)"""
        )
        print("  [OK] LightGBM v1.0 activado como modelo principal")

        conexion.commit()
        print("\n  [OK] Modelos registrados exitosamente!")

    except Exception as e:
        conexion.rollback()
        print(f"  [ERROR] {e}")
        raise
    finally:
        cursor.close()
        conexion.close()


def verificar_registro():
    print("\n[3/3] Verificando registros...")
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT id_modelo, algoritmo, version, estado, mae, rmse, r2, mape FROM modelo_ia ORDER BY id_modelo")
    filas = cursor.fetchall()

    print(f"\n  {'ID':<5} {'Algoritmo':<12} {'Version':<8} {'Estado':<10} {'MAE':>8} {'RMSE':>8} {'R2':>8} {'MAPE':>8}")
    print("  " + "-" * 80)
    for fila in filas:
        print(f"  {fila[0]:<5} {fila[1]:<12} {fila[2]:<8} {fila[3]:<10} {fila[4]:>8.4f} {fila[5]:>8.4f} {fila[6]:>8.4f} {fila[7]:>8.4f}")

    cursor.close()
    conexion.close()


def main():
    print("=" * 60)
    print("REGISTRAR MODELOS EN BASE DE DATOS")
    print("=" * 60)

    copiar_modelos_a_backend()
    registrar_modelos()
    verificar_registro()

    print("\n[OK] Proceso completado!")


if __name__ == "__main__":
    main()
