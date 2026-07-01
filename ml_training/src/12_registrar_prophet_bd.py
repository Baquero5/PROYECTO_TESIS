"""
Script para actualizar ensemble y registrar Prophet en BD
"""
import pymysql
import json
import os

DB_CONFIG = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "123456",
    "database": "tesis_inventario",
    "charset": "utf8mb4"
}

def get_connection():
    return pymysql.connect(**DB_CONFIG, autocommit=False)

def update():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """INSERT INTO modelos_ia (id_dataset, algoritmo, version, archivo_modelo, mae, rmse, r2, mape, estado)
               VALUES (2, 'PROPHET', '2.0', 'prophet_models_dict.pkl', 3.8252, 8.7182, 0.1110, 178.03, 'INACTIVO')"""
        )
        print(f"[OK] Prophet v2.0 registrado (id={cursor.lastrowid})")

        cursor.execute(
            """UPDATE modelos_ia SET estado = 'ACTIVO' 
               WHERE algoritmo = 'LIGHTGBM' AND version = '2.0'"""
        )
        print("[OK] LightGBM v2.0 activado como modelo principal")

        conn.commit()
        print("\n[OK] Prophet registrado y ensemble actualizado!")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("REGISTRAR PROPHET Y ACTUALIZAR ENSEMBLE")
    print("=" * 50)
    update()
