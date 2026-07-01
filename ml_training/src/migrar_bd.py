import pymysql

conn = pymysql.connect(host='localhost', port=3307, user='root', password='123456', database='tesis_inventario', charset='utf8mb4')
cursor = conn.cursor()

migrations = [
    "ALTER TABLE modelos_ia ADD COLUMN archivo_modelo VARCHAR(500) NULL",
    "ALTER TABLE modelos_ia ADD COLUMN parametros TEXT NULL",
    "ALTER TABLE modelos_ia ADD COLUMN estado VARCHAR(20) DEFAULT 'INACTIVO'",
    "ALTER TABLE predicciones ADD COLUMN confianza_min DECIMAL(10,2) NULL",
    "ALTER TABLE predicciones ADD COLUMN confianza_max DECIMAL(10,2) NULL",
    "ALTER TABLE predicciones ADD COLUMN horizonte_dias INT DEFAULT 30",
    "ALTER TABLE predicciones ADD COLUMN porcentaje_confianza DECIMAL(5,2) DEFAULT 95.0",
]

for sql in migrations:
    try:
        cursor.execute(sql)
        col = sql.split("ADD COLUMN ")[1].split(" ")[0]
        table = sql.split("TABLE ")[1].split(" ")[0]
        print(f"[OK] {table}.{col} agregada")
    except Exception as e:
        col = sql.split("ADD COLUMN ")[1].split(" ")[0]
        table = sql.split("TABLE ")[1].split(" ")[0]
        print(f"[SKIP] {table}.{col} ya existe")

conn.commit()
print("\n[OK] Migracion completada!")
cursor.close()
conn.close()
