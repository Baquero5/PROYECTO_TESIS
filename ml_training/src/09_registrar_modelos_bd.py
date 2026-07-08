"""
Script 09: Registrar modelos entrenados en la BD
Lee metricas de metrics/*.json y registros en modelo_ia
"""
import pymysql
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
METRICS_DIR = BASE_DIR / "metrics"

DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "123456",
    "database": "tesis_inventario",
    "charset": "utf8mb4"
}

BACKEND_MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "backend" / "ml_models"


def get_connection():
    return pymysql.connect(**DB_CONFIG, autocommit=False)


def copy_models_to_backend():
    print("[1/3] Copiando modelos a backend/ml_models/...")
    BACKEND_MODELS_DIR.mkdir(parents=True, exist_ok=True)

    model_files = [
        "xgboost_model.pkl",
        "lightgbm_model.pkl",
        "ensemble.pkl",
        "ensemble_weights.pkl",
        "feature_columns.pkl",
    ]

    for filename in model_files:
        src = MODELS_DIR / filename
        dst = BACKEND_MODELS_DIR / filename
        if src.exists():
            import shutil
            shutil.copy2(src, dst)
            size = dst.stat().st_size / 1024
            print(f"  [OK] {filename} ({size:.1f} KB)")
        else:
            print(f"  [SKIP] {filename} no existe")


def register_models():
    print("\n[2/3] Registrando modelos en BD...")
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id_dataset FROM dataset_entrenamiento LIMIT 1")
        result = cursor.fetchone()
        if not result:
            print("  [ERROR] No hay dataset registrado. Ejecuta primero 04_poblar_bd.py")
            return
        dataset_id = result[0]
        print(f"  Dataset ID: {dataset_id}")

        models_to_register = []

        xgb_metrics_path = METRICS_DIR / "xgboost_metrics.json"
        if xgb_metrics_path.exists():
            with open(xgb_metrics_path) as f:
                m = json.load(f)
            models_to_register.append({
                "algoritmo": "XGBOOST",
                "version": "1.0",
                "archivo": "xgboost_model.pkl",
                "mae": m["mae"],
                "rmse": m["rmse"],
                "r2": m.get("r2"),
                "mape": m["mape"],
            })

        lgb_metrics_path = METRICS_DIR / "lightgbm_metrics.json"
        if lgb_metrics_path.exists():
            with open(lgb_metrics_path) as f:
                m = json.load(f)
            models_to_register.append({
                "algoritmo": "LIGHTGBM",
                "version": "1.0",
                "archivo": "lightgbm_model.pkl",
                "mae": m["mae"],
                "rmse": m["rmse"],
                "r2": m.get("r2"),
                "mape": m["mape"],
            })

        ensemble_metrics_path = METRICS_DIR / "ensemble_metrics.json"
        if ensemble_metrics_path.exists():
            with open(ensemble_metrics_path) as f:
                m = json.load(f)
            models_to_register.append({
                "algoritmo": "ENSEMBLE",
                "version": "1.0",
                "archivo": "ensemble.pkl",
                "mae": m["mae"],
                "rmse": m["rmse"],
                "r2": m.get("r2"),
                "mape": m["mape"],
            })

        for model_info in models_to_register:
            cursor.execute(
                "SELECT id_modelo FROM modelo_ia WHERE algoritmo = %s AND version = %s LIMIT 1",
                (model_info["algoritmo"], model_info["version"])
            )
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    """UPDATE modelo_ia
                       SET archivo_modelo = %s, mae = %s, rmse = %s, r2 = %s, mape = %s, estado = 'INACTIVO'
                       WHERE id_modelo = %s""",
                    (model_info["archivo"], model_info["mae"], model_info["rmse"],
                     model_info.get("r2"), model_info["mape"], existing[0])
                )
                print(f"  [OK] {model_info['algoritmo']} v{model_info['version']} actualizado")
            else:
                cursor.execute(
                    """INSERT INTO modelo_ia (id_dataset, algoritmo, version, archivo_modelo, mae, rmse, r2, mape, estado)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (dataset_id, model_info["algoritmo"], model_info["version"], model_info["archivo"],
                     model_info["mae"], model_info["rmse"], model_info.get("r2"), model_info["mape"], "INACTIVO")
                )
                print(f"  [OK] {model_info['algoritmo']} v{model_info['version']} registrado (id={cursor.lastrowid})")

        cursor.execute(
            """UPDATE modelo_ia SET estado = 'ACTIVO'
               WHERE algoritmo = 'LIGHTGBM' AND version = '1.0'
               AND id_modelo = (SELECT id_modelo FROM (SELECT id_modelo FROM modelo_ia WHERE algoritmo = 'LIGHTGBM' AND version = '1.0' LIMIT 1) AS t)"""
        )
        print("  [OK] LightGBM v1.0 activado como modelo principal")

        conn.commit()
        print("\n  [OK] Modelos registrados exitosamente!")

    except Exception as e:
        conn.rollback()
        print(f"  [ERROR] {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def verify_registration():
    print("\n[3/3] Verificando registros...")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id_modelo, algoritmo, version, estado, mae, rmse, r2, mape FROM modelo_ia ORDER BY id_modelo")
    rows = cursor.fetchall()

    print(f"\n  {'ID':<5} {'Algoritmo':<12} {'Version':<8} {'Estado':<10} {'MAE':>8} {'RMSE':>8} {'R2':>8} {'MAPE':>8}")
    print("  " + "-" * 80)
    for row in rows:
        print(f"  {row[0]:<5} {row[1]:<12} {row[2]:<8} {row[3]:<10} {row[4]:>8.4f} {row[5]:>8.4f} {row[6]:>8.4f} {row[7]:>8.4f}")

    cursor.close()
    conn.close()


def main():
    print("=" * 60)
    print("REGISTRAR MODELOS EN BASE DE DATOS")
    print("=" * 60)

    copy_models_to_backend()
    register_models()
    verify_registration()

    print("\n[OK] Proceso completado!")


if __name__ == "__main__":
    main()
