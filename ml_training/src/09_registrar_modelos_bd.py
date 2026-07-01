"""
Script para registrar modelos entrenados v2 en la BD del TESIS
"""
import pymysql
import os
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "123456",
    "database": "tesis_inventario",
    "charset": "utf8mb4"
}

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "backend", "ml_models")

def get_connection():
    return pymysql.connect(**DB_CONFIG, autocommit=False)

def register_models():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id_dataset FROM dataset_entrenamiento LIMIT 1")
        result = cursor.fetchone()
        if not result:
            cursor.execute(
                "INSERT INTO dataset_entrenamiento (nombre_dataset, registros, descripcion) VALUES (%s, %s, %s)",
                ("M5 Walmart - 5 tiendas - 1000 productos", 9425000, "Dataset M5 transformado para entrenamiento ML v2 con features mejorados")
            )
            conn.commit()
            dataset_id = cursor.lastrowid
            print(f"[OK] Dataset creado (id={dataset_id})")
        else:
            dataset_id = result[0]
            print(f"[INFO] Dataset existente (id={dataset_id})")

        models = [
            {
                "algoritmo": "XGBOOST",
                "version": "2.0",
                "archivo": "xgboost_v2_model.pkl",
                "mae": 1.6271,
                "rmse": 3.5007,
                "r2": 0.7268,
                "mape": 69.71,
            },
            {
                "algoritmo": "LIGHTGBM",
                "version": "2.0",
                "archivo": "lightgbm_v2_model.pkl",
                "mae": 1.6279,
                "rmse": 3.5017,
                "r2": 0.7266,
                "mape": 69.52,
            },
            {
                "algoritmo": "XGBOOST",
                "version": "1.0",
                "archivo": "xgboost_model.pkl",
                "mae": 1.658,
                "rmse": 3.6501,
                "r2": 0.722,
                "mape": 70.2522,
            },
            {
                "algoritmo": "LIGHTGBM",
                "version": "1.0",
                "archivo": "lightgbm_model.pkl",
                "mae": 1.6576,
                "rmse": 3.502,
                "r2": 0.7441,
                "mape": 70.7965,
            },
        ]

        for model_info in models:
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
                    (model_info["archivo"], model_info["mae"], model_info["rmse"],
                     model_info.get("r2"), model_info["mape"], existing[0])
                )
                print(f"[OK] {model_info['algoritmo']} v{model_info['version']} actualizado (id={existing[0]})")
            else:
                cursor.execute(
                    """INSERT INTO modelos_ia (id_dataset, algoritmo, version, archivo_modelo, mae, rmse, r2, mape, estado)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (dataset_id, model_info["algoritmo"], model_info["version"], model_info["archivo"],
                     model_info["mae"], model_info["rmse"], model_info.get("r2"), model_info["mape"], "INACTIVO")
                )
                print(f"[OK] {model_info['algoritmo']} v{model_info['version']} registrado (id={cursor.lastrowid})")

        cursor.execute(
            """UPDATE modelos_ia SET estado = 'ACTIVO' 
               WHERE algoritmo = 'LIGHTGBM' AND version = '2.0' 
               AND id_modelo = (SELECT id_modelo FROM (SELECT id_modelo FROM modelos_ia WHERE algoritmo = 'LIGHTGBM' AND version = '2.0' LIMIT 1) AS t)"""
        )
        print("[OK] LightGBM v2.0 activado como modelo principal")

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
    print("REGISTRAR MODELOS v2 EN BASE DE DATOS")
    print("=" * 50)
    register_models()
