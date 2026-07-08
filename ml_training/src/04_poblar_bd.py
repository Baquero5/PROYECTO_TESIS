"""
Script 04: Poblar base de datos MariaDB con datos del M5
Entrada: data/processed/m5_largo.csv
Conexion: root:123456@localhost:3307/INVENTARIO

Restricciones:
- 100 productos max (FOODS, mayor demanda)
- 1 categoria: Alimentos
- 5 subcategorias: Bebidas, Lacteos, Snacks, Abarrotes, Congelados
- 1 proveedor generico
- 5 tiendas
- Nombres en espanol
"""
import pandas as pd
import numpy as np
import pymysql
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import random
import time

BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data" / "processed"

with open(BASE_DIR / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

DB_CONFIG = config["database"]
NUM_PRODUCTOS = 100

# 5 tiendas del M5
TIENDAS_M5 = {
    "CA_1": {"nombre": "Tienda Sacramento", "ciudad": "Sacramento", "estado": "California", "region": "Oeste"},
    "CA_2": {"nombre": "Tienda Los Angeles", "ciudad": "Los Angeles", "estado": "California", "region": "Oeste"},
    "TX_1": {"nombre": "Tienda Houston", "ciudad": "Houston", "estado": "Texas", "region": "Sur"},
    "TX_2": {"nombre": "Tienda Dallas", "ciudad": "Dallas", "estado": "Texas", "region": "Sur"},
    "WI_1": {"nombre": "Tienda Milwaukee", "ciudad": "Milwaukee", "estado": "Wisconsin", "region": "Centro"},
}

# 5 subcategorias en espanol
SUBCATEGORIAS = [
    {"nombre": "Bebidas", "descripcion": "Bebidas y liquidos"},
    {"nombre": "Lacteos", "descripcion": "Productos lacteos y derivados"},
    {"nombre": "Snacks", "descripcion": "Bocadillos y comida rapida"},
    {"nombre": "Abarrotes", "descripcion": "Productos basicos de despensa"},
    {"nombre": "Congelados", "descripcion": "Productos congelados"},
]

# 1 proveedor generico
PROVEEDOR_GENERICO = (
    "Cadena Suministros Walmart",
    "0999999999999",
    "0999999999",
    "suministros@walmart.com",
    "123 Walmart Ave, Bentonville, AR"
)

# Mapeo de subcategorias por palabras clave en el nombre del producto
SUBCAT_KEYWORDS = {
    "Bebidas": [
        "jugo", "agua", "gaseosa", "cerveza", "vino", "sidra", "energizante",
        "te ", "cafe", "leche", "licuado", "smoothie", "kombucha", "malta",
        "limonada", "jamaica", "saborizada", "isotonica", "ginger", "tonica",
        "nescafe", "expresso", "latte", "mocha", "capuccino"
    ],
    "Lacteos": [
        "yogurt", "queso", "mantequilla", "crema", "leche ", "kumis",
        "kefir", "queso", "parmesano", "gouda", "mozzarella", "ricotta",
        "azul", "griego", "condensada", "dulce de leche", "helado",
        "sorbete", "helado"
    ],
    "Snacks": [
        "snack", "papas", "mani", "nueces", "pasas", "palomitas", "chicles",
        "caramelo", "chocolate", "galletas", "barrita", "granola", "muesli",
        "fruta deshidratada", "banana chips", "pistachos", "cacahuates",
        "almendras", "semillas", "torta", "donas", "pan dulce", "croissant",
        "empanada", "pizza", "sopa instantanea"
    ],
    "Abarrotes": [
        "arroz", "aceite", "pan ", "azucar", "sal ", "fideos", "atun",
        "salsa", "mayonesa", "mostaza", "vinagre", "harina", "avena",
        "miel", "mermelada", "champinones", "pimiento", "aceitunas",
        "pepinillos", "achiote", "comino", "pimienta", "oregano",
        "cebolla", "ajo", "pimenton", "curcuma", "canela", "vainilla",
        "bicarbonato", "levadura", "pasta de tomate", "soya", "coco rallado",
        "ketchup", "bbq", "buffalo", "aderezo", "wasabi", "teriyaki",
        "inglesa", "tabasco", "tortillas", "arepa", "pita", "pan integral",
        "sandwich", "wrap", "ensalada", "pure", "guacamole", "hummus",
        "tzatziki", "pico de gallo", "fruta fresca", "verduras", "brocoli",
        "espinaca", "lechuga", "tomate", "pepino", "zanahoria", "ajo fresco",
        "cebolla", "limones", "naranjas", "manzanas", "platanos", "pera",
        "uvas", "fresas", "arandanos", "mango", "pina", "sandia", "melon",
        "aguacate", "clementinas", "carne", "costillas", "pechuga", "muslo",
        "chuleta", "filete", "camarones", "calamar", "pulpo", "salchicha",
        "mortadela", "jamon", "pepperoni", "tocino", "panceta", "huevo",
        "sardinas", "lentejas", "garbanzos", "frijoles", "maiz dulce"
    ],
    "Congelados": [
        "congelad", "hielo", "helado", "sorbete", "empanada congelada",
        "pizza congelada"
    ]
}

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


def clasificar_producto(nombre):
    """Clasifica un producto en subcategoria basado en su nombre."""
    nombre_lower = nombre.lower()
    for subcat, keywords in SUBCAT_KEYWORDS.items():
        for kw in keywords:
            if kw in nombre_lower:
                return subcat
    return "Abarrotes"


def truncate_tables(conn):
    print("[1/8] Limpiando tablas existentes...")
    cursor = conn.cursor()
    tables = [
        "movimientos_inventario",
        "detalle_ventas",
        "ventas",
        "inventarios",
        "productos",
        "subcategorias",
        "tiendas",
        "proveedores",
        "categorias",
        "parametros_inventario",
        "alertas",
        "predicciones",
        "historial_predicciones",
        "modelos_ia",
        "dataset_entrenamiento",
    ]
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  [OK] {table}")
        except Exception as e:
            print(f"  [WARN] {table}: {e}")
    conn.commit()
    cursor.close()


def insert_tendas(conn):
    print("\n[2/8] Insertando tiendas...")
    cursor = conn.cursor()
    tienda_ids = {}
    for store_id, info in TIENDAS_M5.items():
        cursor.execute(
            "INSERT INTO tiendas (nombre, ciudad, estado, region, descripcion) VALUES (%s, %s, %s, %s, %s)",
            (info["nombre"], info["ciudad"], info["estado"], info["region"],
             f"Tienda Walmart en {info['ciudad']}, {info['estado']}")
        )
        tienda_ids[store_id] = cursor.lastrowid
        print(f"  [OK] {info['nombre']} (id={cursor.lastrowid})")
    conn.commit()
    cursor.close()
    return tienda_ids


def insert_categoria(conn):
    print("\n[3/8] Insertando categoria...")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)",
        ("Alimentos", "Productos alimenticios y bebidas")
    )
    cat_id = cursor.lastrowid
    print(f"  [OK] Alimentos (id={cat_id})")
    conn.commit()
    cursor.close()
    return cat_id


def insert_subcategorias(conn, cat_id):
    print("\n[4/8] Insertando subcategorias...")
    cursor = conn.cursor()
    subcat_ids = {}
    for sub in SUBCATEGORIAS:
        cursor.execute(
            "INSERT INTO subcategorias (id_categoria, nombre, descripcion) VALUES (%s, %s, %s)",
            (cat_id, sub["nombre"], sub["descripcion"])
        )
        subcat_ids[sub["nombre"]] = cursor.lastrowid
        print(f"  [OK] {sub['nombre']} (id={cursor.lastrowid})")
    conn.commit()
    cursor.close()
    return subcat_ids


def insert_proveedor(conn):
    print("\n[5/8] Insertando proveedor generico...")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO proveedores (razon_social, ruc, telefono, correo, direccion) VALUES (%s, %s, %s, %s, %s)",
        PROVEEDOR_GENERICO
    )
    prov_id = cursor.lastrowid
    print(f"  [OK] {PROVEEDOR_GENERICO[0]} (id={prov_id})")
    conn.commit()
    cursor.close()
    return prov_id


def insert_productos(conn, unique_items, cat_id, prov_id, subcat_ids):
    print(f"\n[6/8] Insertando {len(unique_items)} productos...")
    cursor = conn.cursor()
    prod_ids_map = {}

    for i, row in unique_items.iterrows():
        nombre = row["nombre"]
        subcat = clasificar_producto(nombre)
        subcat_id = subcat_ids.get(subcat, list(subcat_ids.values())[0])

        precio_venta = float(row.get("price", 5.0))
        if precio_venta <= 0:
            precio_venta = round(random.uniform(1.0, 50.0), 2)
        precio_compra = round(precio_venta * 0.6, 2)

        codigo = f"ALI-{i+1:04d}"

        cursor.execute(
            """INSERT INTO productos (id_categoria, id_subcategoria, id_proveedor, codigo, nombre,
               descripcion, precio_compra, precio_venta, estado)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (cat_id, subcat_id, prov_id, codigo, nombre,
             f"Producto {nombre} - Tienda M5",
             precio_compra, precio_venta, True)
        )
        prod_ids_map[row["item_id"]] = cursor.lastrowid

    conn.commit()
    cursor.close()
    print(f"  [OK] {len(prod_ids_map)} productos insertados")
    return prod_ids_map


def insert_inventarios(conn, prod_ids_map, df, tienda_ids):
    print("\n[7/8] Insertando inventarios por tienda...")
    cursor = conn.cursor()
    count = 0

    for item_id, prod_id in prod_ids_map.items():
        for store_id, tienda_id in tienda_ids.items():
            item_data = df[(df["item_id"] == item_id) & (df["store_id"] == store_id)]
            if item_data.empty:
                stock_actual = 0
            else:
                stock_actual = int(item_data["y"].tail(30).sum())

            stock_minimo = max(10, int(stock_actual * 0.15))
            stock_maximo = int(stock_actual * 2.5)

            cursor.execute(
                """INSERT INTO inventarios (id_producto, id_tienda, stock_actual, stock_minimo, stock_maximo)
                   VALUES (%s, %s, %s, %s, %s)""",
                (prod_id, tienda_id, stock_actual, stock_minimo, stock_maximo)
            )
            count += 1

    conn.commit()
    cursor.close()
    print(f"  [OK] {count} inventarios insertados")


def insert_ventas_y_detalle(conn, df, prod_ids_map, tienda_ids):
    print("\n[8/8] Insertando ventas y detalle de ventas...")
    t0 = time.time()
    cursor = conn.cursor()

    # Incluir todos los registros (incluso y=0) como pide el usuario
    df_daily = df.groupby(["date", "store_id"]).agg(
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
        store_id = row["store_id"]
        tienda_id = tienda_ids.get(store_id)

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

            ventas_batch.append((USUARIO_ID, tienda_id, fecha, round(total_venta, 2)))
            detalles_por_venta.append(detalles)
            venta_count += 1

            if len(ventas_batch) >= batch_size:
                cursor.executemany(
                    "INSERT INTO ventas (id_usuario, id_tienda, fecha_venta, total) VALUES (%s, %s, %s, %s)",
                    ventas_batch
                )
                first_venta_id = cursor.lastrowid

                detalle_with_venta = []
                for i, (venta_base, dets) in enumerate(zip(range(first_venta_id, first_venta_id + len(ventas_batch)), detalles_por_venta)):
                    for det in dets:
                        detalle_with_venta.append((venta_base, det[0], det[1], det[2], det[3]))

                if detalle_with_venta:
                    cursor.executemany(
                        "INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
                        detalle_with_venta
                    )
                    detalle_count += len(detalle_with_venta)

                ventas_batch = []
                detalles_por_venta = []

    if ventas_batch:
        cursor.executemany(
            "INSERT INTO ventas (id_usuario, id_tienda, fecha_venta, total) VALUES (%s, %s, %s, %s)",
            ventas_batch
        )
        first_id = cursor.lastrowid
        remaining_detalles = []
        for i, (venta_base, dets) in enumerate(zip(range(first_id, first_id + len(ventas_batch)), detalles_por_venta)):
            for det in dets:
                remaining_detalles.append((venta_base, det[0], det[1], det[2], det[3]))

        if remaining_detalles:
            cursor.executemany(
                "INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
                remaining_detalles
            )
            detalle_count += len(remaining_detalles)

    conn.commit()
    cursor.close()
    print(f"  [OK] {venta_count:,} ventas insertadas")
    print(f"  [OK] {detalle_count:,} detalles insertados")
    print(f"  Tiempo: {time.time() - t0:.1f}s")


def insert_metadata(conn, num_productos):
    print("\n[Metadata] Insertando metadata de dataset y modelos...")
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO dataset_entrenamiento (nombre_dataset, registros, descripcion)
           VALUES (%s, %s, %s)""",
        (f"M5 Walmart - {len(TIENDAS_M5)} tiendas - {num_productos} productos",
         num_productos,
         f"Dataset M5 transformado. Tiendas: {', '.join(TIENDAS_M5.keys())}. {num_productos} productos FOODS top por demanda.")
    )
    id_dataset = cursor.lastrowid
    print(f"  [OK] Dataset registrado (id={id_dataset})")

    for algoritmo, version in [("XGBoost", "1.0"), ("LightGBM", "1.0")]:
        cursor.execute(
            """INSERT INTO modelos_ia (id_dataset, algoritmo, version)
               VALUES (%s, %s, %s)""",
            (id_dataset, algoritmo, version)
        )
        print(f"  [OK] Modelo {algoritmo} registrado (id={cursor.lastrowid})")

    conn.commit()
    cursor.close()


def main():
    print("=" * 60)
    print("POBLAR BASE DE DATOS - DATOS M5")
    print("=" * 60)
    print(f"  Productos: {NUM_PRODUCTOS} (FOODS, mayor demanda)")
    print(f"  Tiendas: {len(TIENDAS_M5)}")
    print(f"  Subcategorias: {len(SUBCATEGORIAS)}")
    print(f"  Proveedor: 1 generico")
    print(f"  Base de datos: {DB_CONFIG['name']}")
    print("=" * 60)

    print("\nCargando dataset...")
    df = pd.read_csv(PROC_DIR / "m5_largo.csv")
    print(f"  Filas: {df.shape[0]:,}")
    print(f"  Productos unicos: {df['item_id'].nunique()}")
    print(f"  Tiendas: {df['store_id'].unique().tolist()}")

    # Filtrar solo FOODS
    df_foods = df[df["cat_id"] == "FOODS"].copy()
    print(f"  Filas FOODS: {df_foods.shape[0]:,}")

    # Seleccionar top 100 productos por demanda total
    top_items = df_foods.groupby("item_id").agg(
        total_demand=("y", "sum"),
        cat_id=("cat_id", "first"),
        mean_price=("price", "mean")
    ).reset_index().sort_values("total_demand", ascending=False).head(NUM_PRODUCTOS)

    # Nombres descriptivos en espanol para los 100 productos FOODS
    NOMBRES_FOODS = [
        "Leche Entera 1L", "Arroz Premium 5kg", "Aceite Vegetal 1L", "Pan Blanco 600g",
        "Azucar Refinada 1kg", "Sal de Mar 500g", "Fideos Spaghetti 500g", "Atun en Lata 170g",
        "Cafe Molido 250g", "Cereal Integral 375g", "Galletas Digestivas 200g", "Jugo de Naranja 1L",
        "Yogurt Natural 200g", "Mantequilla 200g", "Queso Fresco 500g", "Huevos Docena",
        "Pollo Entero 1.5kg", "Carne Molida 500g", "Chorizo 300g", "Tocino 200g",
        "Sardinas en Lata 150g", "Salsa de Tomate 400g", "Mayonesa 250g", "Mostaza 200g",
        "Vinagre Blanco 500ml", "Harina de Trigo 1kg", "Avena Integral 500g", "Miel Pura 350g",
        "Mermelada Fresa 250g", "Te Negro 100 bolsas", "Chocolate en Polvo 400g",
        "Leche en Polvo 400g", "Crema de Leche 200ml", "Agua Mineral 1.5L", "Gaseosa Cola 2L",
        "Cerveza Artesanal 355ml", "Vino Tinto 750ml", "Sidra Natural 330ml", "Energizante 250ml",
        "Snack Papas 150g", "Mani Salado 200g", "Nueces Mix 150g", "Pasas 200g",
        "Duraznos en Almibar 500g", "Maiz Dulce 300g", "Frijoles Negros 400g", "Lentejas 500g",
        "Garbanzos 400g", "Champinones 200g", "Pimiento Morron 200g", "Aceitunas Verdes 250g",
        "Pepinillos 350g", "Sopa Instantanea 85g", "Caldo de Pollo 1L", "Achiote 100g",
        "Comino Molido 50g", "Pimienta Negra 50g", "Oregano Seco 30g", "Cebolla Deshidratada 50g",
        "Ajo en Polvo 50g", "Pimenton Dulce 50g", "Curcuma 50g", "Canela en Polvo 50g",
        "Vainilla Esencia 100ml", "Bicarbonato 500g", "Levadura Seca 100g",
        "Aceite de Oliva 500ml", "Pasta de Tomate 200g", "Salsa de Soya 250ml",
        "Coco Rallado 200g", "Almendras 150g", "Semillas de Girasol 200g",
        "Pistachos 100g", "Cacahuates 250g", "Granola 375g", "Barrita de Cereal 6uds",
        "Muesli 500g", "Fruta Deshidratada 200g", "Banana Chips 100g",
        "Papa Frita 100g", "Palomitas de Maiz 100g", "Chicles 12uds", "Caramelo 200g",
        "Chocolate Negro 100g", "Chocolate con Leche 100g", "Galletas de Vainilla 150g",
        "Torta en Porcion 120g", "Donas 6uds", "Pan Dulce 400g", "Croissant 4uds",
        "Empanadas Congeladas 6uds", "Pizza Congelada 400g", "Helado Vainilla 1L",
        "Helado Chocolate 1L", "Helado Fresa 1L", "Sorbete de Lima 500ml",
        "Hielo Bolsa 1kg", "Leche de Soya 1L", "Leche de Almendras 1L",
        "Jugo de Manzana 1L", "Jugo de Uva 1L", "Nectar de Durazno 1L",
        "Cafe Instantaneo 100g", "Cafe en Grano 250g", "Cafe Descafeinado 200g",
        "Te Verde 50 bolsas", "Te de Manzanilla 50 bolsas", "Infusion Frutas 25 bolsas",
        "Leche Condensada 397g", "Dulce de Leche 400g", "Mermelada de Durazno 250g",
    ]

    # Asignar nombres a los top items
    top_items["nombre"] = [NOMBRES_FOODS[i % len(NOMBRES_FOODS)] for i in range(len(top_items))]

    # Filtrar df para incluir solo los 100 productos seleccionados
    selected_item_ids = top_items["item_id"].tolist()
    df_filtered = df_foods[df_foods["item_id"].isin(selected_item_ids)].copy()

    conn = get_connection()
    try:
        truncate_tables(conn)
        tienda_ids = insert_tendas(conn)
        cat_id = insert_categoria(conn)
        subcat_ids = insert_subcategorias(conn, cat_id)
        prov_id = insert_proveedor(conn)
        prod_ids_map = insert_productos(conn, top_items, cat_id, prov_id, subcat_ids)
        insert_inventarios(conn, prod_ids_map, df_filtered, tienda_ids)
        insert_ventas_y_detalle(conn, df_filtered, prod_ids_map, tienda_ids)
        insert_metadata(conn, len(prod_ids_map))

        print("\n" + "=" * 60)
        print("BASE DE DATOS POBLADA EXITOSAMENTE!")
        print("=" * 60)
        print(f"  Tiendas: {len(tienda_ids)}")
        print(f"  Categoria: 1 (Alimentos)")
        print(f"  Subcategorias: {len(subcat_ids)}")
        print(f"  Proveedor: 1 (generico)")
        print(f"  Productos: {len(prod_ids_map)}")
        print(f"  Conexion: {DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['name']}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
