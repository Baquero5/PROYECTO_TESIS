"""
Script 04: Poblar base de datos MariaDB con datos del M5
Entrada: data/processed/m5_largo.csv
 Conexion: root:123456@localhost:3307/tesis_inventario
Categorias: Enlatados y Conservas, Empacados, Frescos
"""
import pandas as pd
import numpy as np
import pymysql
import yaml
import random
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data" / "processed"

with open(BASE_DIR / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

DB_CONFIG = config["database"]
TIENDAS = config["dataset"]["tiendas"]
TIENDAS_NOMBRES = config["dataset"]["tiendas_nombres"]
SUBCATS = config["dataset"]["subcategorias"]

NOMBRES_POR_SUBCAT = {
    "FOODS_1": [
        "Frijoles Negros 400g", "Frijoles Rojos 400g", "Lentejas 500g", "Garbanzos 400g",
        "Atun en Lata 170g", "Sardinas 150g", "Sopa Instantanea 85g", "Sopa de Pollo 500ml",
        "Sopa de Tomate 500ml", "Crema de Champiñones 500ml", "Champiñones 200g",
        "Pimiento Morron 200g", "Aceitunas Verdes 250g", "Pepinillos 350g",
        "Salsa de Tomate 400g", "Pasta de Tomate 200g", "Mayonesa 250g",
        "Mostaza 200g", "Vinagre Blanco 500ml", "Ketchup 500ml",
        "Salsa BBQ 350ml", "Salsa de Soya 250ml", "Salsa Inglesa 150ml",
        "Duraznos en Almibar 500g", "Maiz Dulce 300g", "Menestra Lenteja 500g",
        "Conserva de Verduras 400g", "Puré de Papas 200g", "Caldo de Pollo 1L",
        "Caldo de Res 1L", "Atun en Aceite 170g", "Cocktail de Frutas 500g",
        "Leche de Coco 400ml", "Tomate Entero 400g", "Arvejas Enlatadas 200g",
        "Choclo Entero 300g", "Espinaca Baby 150g", "Brocoli Fresco 300g",
    ],
    "FOODS_2": [
        "Arroz Premium 5kg", "Arroz Blanco 1kg", "Fideos Spaghetti 500g",
        "Fideos Cortos 500g", "Harina de Trigo 1kg", "Azucar Refinada 1kg",
        "Sal de Mar 500g", "Avena Integral 500g", "Cereal Integral 375g",
        "Granola 375g", "Cafe Molido 250g", "Cafe Instantaneo 100g",
        "Te Negro 100 bolsas", "Te Verde 50 bolsas", "Chocolate en Polvo 400g",
        "Leche en Polvo 400g", "Galletas Digestivas 200g", "Galletas de Vainilla 150g",
        "Pan Dulce 400g", "Barrita de Cereal 6uds", "Muesli 500g",
        "Pasas 200g", "Mani Salado 200g", "Nueces Mix 150g",
        "Semillas de Girasol 200g", "Almendras 150g", "Cacahuates 250g",
        "Coco Rallado 200g", "Leche Condensada 397g", "Dulce de Leche 400g",
        "Miel Pura 350g", "Sirope de Arce 250ml", "Aceite de Oliva 500ml",
        "Aceite Vegetal 1L", "Aceite de Coco 200ml", "Canela en Polvo 50g",
        "Comino Molido 50g", "Pimienta Negra 50g", "Orégano Seco 30g",
    ],
    "FOODS_3": [
        "Leche Entera 1L", "Leche Descremada 1L", "Leche Semidescremada 1L",
        "Yogurt Natural 200g", "Yogurt Griego 170g", "Yogurt de Fresa 170g",
        "Queso Fresco 500g", "Queso Mozzarella 250g", "Queso Gouda 200g",
        "Mantequilla 200g", "Crema de Leche 200ml", "Huevos Docena",
        "Pan Blanco 600g", "Pan Integral 600g", "Pan de Molde 500g",
        "Jugo de Naranja 1L", "Jugo de Manzana 1L", "Gaseosa Cola 2L",
        "Agua Mineral 1.5L", "Limonada Natural 1L", "Pollo Entero 1.5kg",
        "Pechuga de Pollo 1kg", "Muslo de Pollo 1kg", "Carne de Res 1kg",
        "Carne Molida 500g", "Chorizo 300g", "Tocino 200g",
        "Salchicha 500g", "Jamón 300g", "Mortadela 300g",
        "Fruta Fresca Mix 500g", "Platanos 1kg", "Manzanas 4uds",
        "Naranjas 4uds", "Limones 4uds", "Uvas 500g",
        "Fresas 250g", "Pera 4uds", "Mango 2uds", "Sandia 1ud",
        "Tomate Cherry 250g", "Lechuga Romana 300g", "Zanahoria Baby 250g",
        "Pepino Importado 2uds", "Cebolla Blanca 3uds", "Ajo Fresco 3uds",
        "Champiñones Frescos 200g", "Aguacate 2uds", "Piña 1ud", "Melon 1ud",
    ],
}

PROVEEDORES = [
    ("Distribuidora Central S.A.", "0991234567001", "0991234567", "contacto@distribcentral.com", "Av. Principal 123, Guayaquil"),
    ("Mayorista Norte C.L.", "0991234567002", "0991234568", "ventas@mayoristanorte.com", "Av. Norte 456, Quito"),
    ("Alimentos Frescos del Sur", "0991234567003", "0991234569", "pedidos@frescossur.com", "Calle Sur 789, Cuenca"),
    ("Importadora Global", "0991234567004", "0991234570", "info@globalimport.com", "Zona Industrial, Ambato"),
    ("Distribuidora Amazonia", "0991234567005", "0991234571", "ventas@amazonia.com", "Av. Amazonas 321, Loja"),
]

USUARIO_ID = 1


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


def truncate_tables(conn):
    print("[1/8] Limpiando tablas existentes...")
    cursor = conn.cursor()
    tables = [
        "movimiento_inventario",
        "detalle_venta",
        "venta",
        "inventario",
        "producto",
        "proveedor",
        "categoria",
        "alerta",
        "prediccion",
        "modelo_ia",
        "dataset_entrenamiento",
        "parametro_inventario",
        "reabastecimiento",
        "historial_prediccion",
    ]
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  [OK] {table}")
        except Exception as e:
            print(f"  [WARN] {table}: {e}")
    conn.commit()
    cursor.close()


def insert_categorias(conn):
    print("\n[2/8] Insertando categorias...")
    cursor = conn.cursor()
    cat_ids = {}
    for dept_code, info in SUBCATS.items():
        cursor.execute(
            "INSERT INTO categoria (nombre, descripcion) VALUES (%s, %s)",
            (info["nombre"], info["descripcion"])
        )
        cat_ids[dept_code] = cursor.lastrowid
        print(f"  [OK] {info['nombre']} (id={cursor.lastrowid})")
    conn.commit()
    cursor.close()
    return cat_ids


def insert_proveedores(conn):
    print("\n[3/8] Insertando proveedores...")
    cursor = conn.cursor()
    prov_ids = []
    for prov in PROVEEDORES:
        cursor.execute(
            "INSERT INTO proveedor (razon_social, ruc, telefono, correo, direccion) VALUES (%s, %s, %s, %s, %s)",
            prov
        )
        prov_ids.append(cursor.lastrowid)
        print(f"  [OK] {prov[0]} (id={cursor.lastrowid})")
    conn.commit()
    cursor.close()
    return prov_ids


def get_nombre_producto(dept_id, index):
    nombres = NOMBRES_POR_SUBCAT.get(dept_id, [])
    if index < len(nombres):
        return nombres[index]
    return f"Producto {dept_id}_{index+1:03d}"


def insert_productos(conn, df_items, cat_ids, prov_ids):
    print(f"\n[4/8] Insertando productos...")
    cursor = conn.cursor()
    prod_ids_map = {}

    unique_items = df_items.groupby("item_id").first().reset_index()

    subcat_counters = {dept: 0 for dept in SUBCATS.keys()}

    SUBCAT_PREFIX = {
        "FOODS_1": "ENL",
        "FOODS_2": "EMP",
        "FOODS_3": "FRE",
    }

    for idx, (_, row) in enumerate(unique_items.iterrows()):
        dept_id = row["dept_id"]
        cat_id = cat_ids.get(dept_id, list(cat_ids.values())[0])
        prov_id = prov_ids[idx % len(prov_ids)]

        precio_venta = float(row.get("price", 5.0))
        if precio_venta <= 0:
            precio_venta = round(random.uniform(1.0, 25.0), 2)
        precio_compra = round(precio_venta * 0.6, 2)

        nombre = get_nombre_producto(dept_id, subcat_counters[dept_id])
        subcat_counters[dept_id] += 1

        prefix = SUBCAT_PREFIX.get(dept_id, "PRO")
        codigo = f"{prefix}-{subcat_counters[dept_id]:03d}"

        cursor.execute(
            """INSERT INTO producto (id_categoria, id_proveedor, codigo, nombre,
               descripcion, precio_compra, precio_venta, estado)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (cat_id, prov_id, codigo, nombre,
             f"{nombre} - {SUBCATS[dept_id]['nombre']}",
             precio_compra, precio_venta, True)
        )
        prod_ids_map[row["item_id"]] = cursor.lastrowid

    conn.commit()
    cursor.close()
    print(f"  [OK] {len(prod_ids_map)} productos insertados")
    return prod_ids_map


def insert_inventarios(conn, prod_ids_map, df):
    print("\n[5/8] Insertando inventarios...")
    cursor = conn.cursor()
    count = 0

    for item_id, prod_id in prod_ids_map.items():
        item_data = df[df["item_id"] == item_id]
        if item_data.empty:
            continue

        stock_actual = int(item_data["y"].tail(30).sum())
        stock_minimo = max(10, int(stock_actual * 0.15))
        stock_maximo = int(stock_actual * 2.5)

        cursor.execute(
            """INSERT INTO inventario (id_producto, stock_actual, stock_minimo, stock_maximo)
               VALUES (%s, %s, %s, %s)""",
            (prod_id, stock_actual, stock_minimo, stock_maximo)
        )
        count += 1

    conn.commit()
    cursor.close()
    print(f"  [OK] {count} inventarios insertados")


def insert_ventas_y_detalle(conn, df, prod_ids_map):
    print("\n[6/8] Insertando ventas y detalle de ventas...")
    t0 = time.time()
    cursor = conn.cursor()

    df_ventas = df[df["y"] > 0].copy()
    df_daily = df_ventas.groupby(["date", "store_id"]).agg(
        items=("item_id", list),
        quantities=("y", list),
        prices=("price", list)
    ).reset_index()

    venta_count = 0
    detalle_count = 0
    batch_size = 500

    ventas_batch = []
    detalles_por_venta = []

    for _, row in df_daily.iterrows():
        total_venta = 0.0
        detalles = []

        for item_id, qty, price in zip(row["items"], row["quantities"], row["prices"]):
            if item_id in prod_ids_map and qty > 0 and price > 0:
                subtotal = float(qty) * float(price)
                total_venta += subtotal
                detalles.append((
                    prod_ids_map[item_id],
                    int(qty),
                    float(price),
                    round(subtotal, 2)
                ))

        if total_venta > 0:
            fecha = row["date"]
            if isinstance(fecha, str):
                fecha = pd.to_datetime(fecha).date()
            elif hasattr(fecha, "date"):
                fecha = fecha.date()

            ventas_batch.append((USUARIO_ID, fecha, round(total_venta, 2)))
            detalles_por_venta.append(detalles)
            venta_count += 1

            if len(ventas_batch) >= batch_size:
                cursor.executemany(
                    "INSERT INTO venta (id_usuario, fecha_venta, total) VALUES (%s, %s, %s)",
                    ventas_batch
                )
                first_id = cursor.lastrowid

                detalle_with_venta = []
                for i, (venta_base, dets) in enumerate(zip(range(first_id, first_id + len(ventas_batch)), detalles_por_venta)):
                    for det in dets:
                        detalle_with_venta.append((venta_base, det[0], det[1], det[2], det[3]))

                if detalle_with_venta:
                    cursor.executemany(
                        "INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
                        detalle_with_venta
                    )
                    detalle_count += len(detalle_with_venta)

                ventas_batch = []
                detalles_por_venta = []

    if ventas_batch:
        cursor.executemany(
            "INSERT INTO venta (id_usuario, fecha_venta, total) VALUES (%s, %s, %s)",
            ventas_batch
        )
        first_id = cursor.lastrowid
        remaining_detalles = []
        for i, (venta_base, dets) in enumerate(zip(range(first_id, first_id + len(ventas_batch)), detalles_por_venta)):
            for det in dets:
                remaining_detalles.append((venta_base, det[0], det[1], det[2], det[3]))

        if remaining_detalles:
            cursor.executemany(
                "INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
                remaining_detalles
            )
            detalle_count += len(remaining_detalles)

    conn.commit()
    cursor.close()
    print(f"  [OK] {venta_count:,} ventas insertadas")
    print(f"  [OK] {detalle_count:,} detalles insertados")
    print(f"  Tiempo: {time.time() - t0:.1f}s")


def insert_movimientos(conn, df, prod_ids_map):
    print("\n[7/8] Insertando movimientos de inventario...")
    t0 = time.time()
    cursor = conn.cursor()

    batch = []
    batch_size = 1000

    for item_id, prod_id in prod_ids_map.items():
        item_data = df[(df["item_id"] == item_id) & (df["y"] > 0)].sort_values("date")

        stock_acumulado = 0
        for _, row in item_data.head(1).iterrows():
            cantidad = int(row["y"]) * 3
            fecha = row["date"]
            if hasattr(fecha, "to_pydatetime"):
                fecha = fecha.to_pydatetime()
            batch.append((prod_id, "ENTRADA", cantidad, fecha, "Reabastecimiento inicial"))
            stock_acumulado = cantidad

        for _, row in item_data.iterrows():
            cantidad = int(row["y"])
            fecha = row["date"]
            if hasattr(fecha, "to_pydatetime"):
                fecha = fecha.to_pydatetime()

            batch.append((prod_id, "SALIDA", cantidad, fecha, "Venta registrada"))
            stock_acumulado -= cantidad

            if stock_acumulado < 20:
                reposicion = cantidad * 3
                batch.append((prod_id, "ENTRADA", reposicion, fecha, "Reabastecimiento automatico"))
                stock_acumulado += reposicion

            if len(batch) >= batch_size:
                cursor.executemany(
                    """INSERT INTO movimiento_inventario (id_producto, tipo_movimiento, cantidad, fecha_movimiento, observacion)
                       VALUES (%s, %s, %s, %s, %s)""",
                    batch
                )
                batch = []

    if batch:
        cursor.executemany(
            """INSERT INTO movimiento_inventario (id_producto, tipo_movimiento, cantidad, fecha_movimiento, observacion)
               VALUES (%s, %s, %s, %s, %s)""",
            batch
        )

    conn.commit()
    cursor.close()
    print(f"  Movimientos insertados en {time.time() - t0:.1f}s")


def insert_metadata(conn, df):
    print("\n[8/8] Insertando metadata de dataset y modelos...")
    cursor = conn.cursor()

    num_productos = df["item_id"].nunique()
    num_registros = df.shape[0]

    tiendas_str = ", ".join(TIENDAS)
    subcats_str = ", ".join([info["nombre"] for info in SUBCATS.values()])

    cursor.execute(
        """INSERT INTO dataset_entrenamiento (nombre_dataset, registros, descripcion)
           VALUES (%s, %s, %s)""",
        (f"M5 Alimentos - {len(TIENDAS)} tiendas - {num_productos} productos",
         num_registros,
         f"Dataset M5 filtrado. Tiendas: {tiendas_str}. Subcategorias: {subcats_str}. {num_productos} productos.")
    )
    id_dataset = cursor.lastrowid
    print(f"  [OK] Dataset registrado (id={id_dataset})")

    for algoritmo, version in [("XGBOOST", "1.0"), ("LIGHTGBM", "1.0")]:
        cursor.execute(
            """INSERT INTO modelo_ia (id_dataset, algoritmo, version)
               VALUES (%s, %s, %s)""",
            (id_dataset, algoritmo, version)
        )
        print(f"  [OK] Modelo {algoritmo} v{version} registrado (id={cursor.lastrowid})")

    conn.commit()
    cursor.close()


def main():
    print("=" * 60)
    print("POBLAR BASE DE DATOS - DATOS M5")
    print("=" * 60)

    print("\nCargando dataset...")
    df = pd.read_csv(PROC_DIR / "m5_largo.csv")
    print(f"  Filas: {df.shape[0]:,}")
    print(f"  Productos unicos: {df['item_id'].nunique()}")
    print(f"  Tiendas: {df['store_id'].unique().tolist()}")

    unique_items = df.groupby("item_id").agg(
        total_demand=("y", "sum"),
        cat_id=("cat_id", "first"),
        dept_id=("dept_id", "first"),
        price=("price", "mean")
    ).reset_index().sort_values("total_demand", ascending=False)

    conn = get_connection()
    try:
        truncate_tables(conn)
        cat_ids = insert_categorias(conn)
        prov_ids = insert_proveedores(conn)
        prod_ids_map = insert_productos(conn, unique_items, cat_ids, prov_ids)
        insert_inventarios(conn, prod_ids_map, df)
        insert_ventas_y_detalle(conn, df, prod_ids_map)
        insert_movimientos(conn, df, prod_ids_map)
        insert_metadata(conn, df)

        print("\n" + "=" * 60)
        print("BASE DE DATOS POBLADA EXITOSAMENTE!")
        print("=" * 60)
        print(f"  Categorias: {len(cat_ids)}")
        print(f"  Proveedores: {len(prov_ids)}")
        print(f"  Productos: {len(prod_ids_map)}")
        print(f"  Conexion: {DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['name']}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
