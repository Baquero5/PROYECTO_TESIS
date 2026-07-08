"""
Script 09: Registrar modelos entrenados en la BD
Entrada: models/*.pkl, metrics/comparativa_modelos.json
Conexion: root:123456@localhost:3307/INVENTARIO
"""
import pymysql
import yaml
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

DB_CONFIG = config["database"]
METRICS_DIR = BASE_DIR / "metrics"
MODELS_DIR = BASE_DIR / "models"


def get_connection():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["name"],
        charset="utf8mb4",
        autocommit=False
    )


def load_metrics():
    metrics_file = METRICS_DIR / "comparativa_modelos.json"
    if not metrics_file.exists():
        print(f"[ERROR] No se encontro: {metrics_file}")
        print("  Ejecuta primero 07_evaluar_modelos.py")
        return None

    with open(metrics_file, "r") as f:
        data = json.load(f)
    print(f"[OK] Metricas cargadas: {metrics_file}")
    return data


def register_models():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Verificar dataset existente
        cursor.execute("SELECT id_dataset FROM dataset_entrenamiento LIMIT 1")
        result = cursor.fetchone()
        if not result:
            print("[ERROR] No hay dataset registrado. Ejecuta primero 04_poblar_bd.py")
            return
        dataset_id = result[0]
        print(f"[INFO] Dataset existente (id={dataset_id})")

        # Cargar metricas
        metrics = load_metrics()
        if metrics is None:
            return

        # Registrar modelos v1
        models = [
            {
                "algoritmo": "XGBOOST",
                "version": "1.0",
                "archivo": "xgboost_model.pkl",
            },
            {
                "algoritmo": "LIGHTGBM",
                "version": "1.0",
                "archivo": "lightgbm_model.pkl",
            },
        ]

        for model_info in models:
            algo_key = model_info["algoritmo"].lower()
            algo_metrics = metrics.get(algo_key, {})

            if not algo_metrics:
                print(f"[WARN] No se encontraron metricas para {model_info['algoritmo']}")
                continue

            mae = algo_metrics.get("mae")
            rmse = algo_metrics.get("rmse")
            r2 = algo_metrics.get("r2")
            mape = algo_metrics.get("mape")

            cursor.execute(
                "SELECT id_modelo FROM modelos_ia WHERE algoritmo = %s AND version = %s LIMIT 1",
                (model_info["algoritmo"], model_info["version"])
            )
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    """UPDATE modelos_ia
                       SET archivo_modelo = %s, mae = %s, rmse = %s, r2 = %s, mape = %s, estado = 'INACTIVO'
                       WHERE id_modelo = %s""",
                    (model_info["archivo"], mae, rmse, r2, mape, existing[0])
                )
                print(f"[OK] {model_info['algoritmo']} v{model_info['version']} actualizado (id={existing[0]})")
            else:
                cursor.execute(
                    """INSERT INTO modelos_ia (id_dataset, algoritmo, version, archivo_modelo, mae, rmse, r2, mape, estado)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (dataset_id, model_info["algoritmo"], model_info["version"], model_info["archivo"],
                     mae, rmse, r2, mape, "INACTIVO")
                )
                print(f"[OK] {model_info['algoritmo']} v{model_info['version']} registrado (id={cursor.lastrowid})")

        # Activar LightGBM como modelo principal
        cursor.execute(
            """UPDATE modelos_ia SET estado = 'ACTIVO'
               WHERE algoritmo = 'LIGHTGBM' AND version = '1.0'
               AND id_modelo = (SELECT id_modelo FROM (SELECT id_modelo FROM modelos_ia WHERE algoritmo = 'LIGHTGBM' AND version = '1.0' LIMIT 1) AS t)"""
        )
        print("[OK] LightGBM v1.0 activado como modelo principal")

        conn.commit()
        print("\n[OK] Modelos registrados exitosamente!")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("=" * 50)
    print("REGISTRAR MODELOS EN BASE DE DATOS")
    print("=" * 50)
    register_models()
