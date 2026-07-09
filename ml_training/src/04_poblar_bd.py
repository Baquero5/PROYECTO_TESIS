"""
Script 04: Poblar base de datos MariaDB con datos del M5
Entrada: data/processed/m5_largo.csv
Conexion: root:123456@localhost:3307/TESIS
Categoria: Alimentos (con 3 subcategorias)
"""
import pandas as pd
import numpy as np
import pymysql
import yaml
import random
import time
from pathlib import Path
from datetime import datetime

DIRECTORIO_BASE = Path(__file__).resolve().parent.parent
DIRECTORIO_PROCESADO = DIRECTORIO_BASE / "data" / "processed"

with open(DIRECTORIO_BASE / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

DB_CONFIG = config["database"]
TIENDAS = config["dataset"]["tiendas"]
TIENDAS_NOMBRES = config["dataset"]["tiendas_nombres"]
SUBCATS = config["dataset"]["subcategorias"]
CATEGORIA_PRINCIPAL = config["dataset"]["categoria_principal"]

NOMBRES_POR_SUBCAT = {
    "FOODS_1": [
        "Frijoles Negros 400g", "Frijoles Rojos 400g", "Lentejas 500g", "Garbanzos 400g",
        "Atun en Lata 170g", "Sardinas 150g", "Sopa Instantanea 85g", "Sopa de Pollo 500ml",
        "Sopa de Tomate 500ml", "Crema de Champinones 500ml", "Champinones 200g",
        "Pimiento Morron 200g", "Aceitunas Verdes 250g", "Pepinillos 350g",
        "Salsa de Tomate 400g", "Pasta de Tomate 200g", "Mayonesa 250g",
        "Mostaza 200g", "Vinagre Blanco 500ml", "Ketchup 500ml",
        "Salsa BBQ 350ml", "Salsa de Soya 250ml", "Salsa Inglesa 150ml",
        "Duraznos en Almibar 500g", "Maiz Dulce 300g", "Menestra Lenteja 500g",
        "Conserva de Verduras 400g", "Pure de Papas 200g", "Caldo de Pollo 1L",
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
        "Comino Molido 50g", "Pimienta Negra 50g", "Oregano Seco 30g",
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
        "Salchicha 500g", "Jamon 300g", "Mortadela 300g",
        "Fruta Fresca Mix 500g", "Platanos 1kg", "Manzanas 4uds",
        "Naranjas 4uds", "Limones 4uds", "Uvas 500g",
        "Fresas 250g", "Pera 4uds", "Mango 2uds", "Sandia 1ud",
        "Tomate Cherry 250g", "Lechuga Romana 300g", "Zanahoria Baby 250g",
        "Pepino Importado 2uds", "Cebolla Blanca 3uds", "Ajo Fresco 3uds",
        "Champinones Frescos 200g", "Aguacate 2uds", "Pina 1ud", "Melon 1ud",
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


def obtener_conexion():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["name"],
        charset="utf8mb4",
        autocommit=False
    )


def vaciar_tablas(conexion):
    print("[1/8] Limpiando tablas existentes...")
    cursor = conexion.cursor()
    tablas = [
        "movimiento_inventario",
        "detalle_venta",
        "venta",
        "inventario",
        "producto",
        "subcategoria",
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
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for tabla in tablas:
        try:
            cursor.execute(f"TRUNCATE TABLE {tabla}")
            print(f"  [OK] {tabla}")
        except Exception as e:
            print(f"  [WARN] {tabla}: {e}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conexion.commit()
    cursor.close()


def insertar_categoria(conexion):
    print("\n[2/8] Insertando categoria principal...")
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO categoria (nombre, descripcion) VALUES (%s, %s)",
        (CATEGORIA_PRINCIPAL, "Productos alimenticios y bebidas")
    )
    id_categoria = cursor.lastrowid
    print(f"  [OK] {CATEGORIA_PRINCIPAL} (id={id_categoria})")
    conexion.commit()
    cursor.close()
    return id_categoria


def insertar_subcategorias(conexion, id_categoria):
    print("\n[3/8] Insertando subcategorias...")
    cursor = conexion.cursor()
    ids_subcategorias = {}
    for codigo, info in SUBCATS.items():
        cursor.execute(
            "INSERT INTO subcategoria (id_categoria, nombre, descripcion) VALUES (%s, %s, %s)",
            (id_categoria, info["nombre"], info["descripcion"])
        )
        ids_subcategorias[codigo] = cursor.lastrowid
        print(f"  [OK] {info['nombre']} (id={cursor.lastrowid})")
    conexion.commit()
    cursor.close()
    return ids_subcategorias


def insertar_usuario_defecto(conexion):
    print("\n[5/8] Insertando usuario por defecto...")
    cursor = conexion.cursor()
    
    # Crear rol ADMINISTRADOR si no existe
    cursor.execute("SELECT id_rol FROM rol WHERE nombre = 'ADMINISTRADOR'")
    resultado = cursor.fetchone()
    if resultado:
        id_rol = resultado[0]
    else:
        cursor.execute("INSERT INTO rol (nombre, descripcion) VALUES ('ADMINISTRADOR', 'Administrador del sistema')")
        id_rol = cursor.lastrowid
    
    # Crear usuario admin si no existe
    cursor.execute("SELECT id_usuario FROM usuario WHERE correo = 'admin@sistema.com'")
    resultado = cursor.fetchone()
    if resultado:
        id_usuario = resultado[0]
        print(f"  [OK] Usuario admin ya existe (id={id_usuario})")
    else:
        from passlib.hash import bcrypt
        password_hash = bcrypt.hash("Admin123!")
        cursor.execute(
            "INSERT INTO usuario (id_rol, nombres, apellidos, correo, password_hash, estado) VALUES (%s, 'Administrador', 'del Sistema', 'admin@sistema.com', %s, 1)",
            (id_rol, password_hash)
        )
        id_usuario = cursor.lastrowid
        print(f"  [OK] Usuario admin creado (id={id_usuario})")
    
    conexion.commit()
    cursor.close()
    return id_usuario


def insertar_proveedores(conexion):
    print("\n[4/8] Insertando proveedores...")
    cursor = conexion.cursor()
    ids_proveedores = []
    for prov in PROVEEDORES:
        cursor.execute(
            "INSERT INTO proveedor (razon_social, ruc, telefono, correo, direccion) VALUES (%s, %s, %s, %s, %s)",
            prov
        )
        ids_proveedores.append(cursor.lastrowid)
        print(f"  [OK] {prov[0]} (id={cursor.lastrowid})")
    conexion.commit()
    cursor.close()
    return ids_proveedores


def obtener_nombre_producto(dept_id, indice):
    nombres = NOMBRES_POR_SUBCAT.get(dept_id, [])
    if indice < len(nombres):
        return nombres[indice]
    return f"Producto {dept_id}_{indice+1:03d}"


def insertar_productos(conexion, productos_unicos, id_categoria, ids_subcategorias, ids_proveedores):
    print(f"\n[5/8] Insertando productos...")
    cursor = conexion.cursor()
    mapa_productos = {}

    SUBCAT_PREFIJO = {
        "FOODS_1": "ENL",
        "FOODS_2": "EMP",
        "FOODS_3": "FRE",
    }

    contadores_subcat = {dept: 0 for dept in SUBCATS.keys()}

    for idx, (_, fila) in enumerate(productos_unicos.iterrows()):
        dept_id = fila["dept_id"]
        id_sub = ids_subcategorias.get(dept_id, list(ids_subcategorias.values())[0])
        id_prov = ids_proveedores[idx % len(ids_proveedores)]

        precio_venta = float(fila.get("price", 5.0))
        if precio_venta <= 0:
            precio_venta = round(random.uniform(1.0, 25.0), 2)
        precio_compra = round(precio_venta * 0.6, 2)

        nombre = obtener_nombre_producto(dept_id, contadores_subcat[dept_id])
        contadores_subcat[dept_id] += 1

        prefijo = SUBCAT_PREFIJO.get(dept_id, "PRO")
        codigo = f"{prefijo}-{contadores_subcat[dept_id]:03d}"

        cursor.execute(
            """INSERT INTO producto (id_categoria, id_subcategoria, id_proveedor, codigo, nombre,
               descripcion, precio_compra, precio_venta, estado)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (id_categoria, id_sub, id_prov, codigo, nombre,
             f"{nombre} - {SUBCATS[dept_id]['nombre']}",
             precio_compra, precio_venta, True)
        )
        mapa_productos[fila["item_id"]] = cursor.lastrowid

    conexion.commit()
    cursor.close()
    print(f"  [OK] {len(mapa_productos)} productos insertados")
    return mapa_productos


def insertar_inventarios(conexion, mapa_productos, df):
    print("\n[6/8] Insertando inventarios...")
    cursor = conexion.cursor()
    contador = 0

    for item_id, prod_id in mapa_productos.items():
        datos_item = df[df["item_id"] == item_id]
        if datos_item.empty:
            continue

        stock_actual = int(datos_item["y"].tail(30).sum())
        stock_minimo = max(10, int(stock_actual * 0.15))
        stock_maximo = int(stock_actual * 2.5)

        cursor.execute(
            """INSERT INTO inventario (id_producto, stock_actual, stock_minimo, stock_maximo)
               VALUES (%s, %s, %s, %s)""",
            (prod_id, stock_actual, stock_minimo, stock_maximo)
        )
        contador += 1

    conexion.commit()
    cursor.close()
    print(f"  [OK] {contador} inventarios insertados")


def insertar_ventas_y_detalle(conexion, df, mapa_productos):
    print("\n[7/8] Insertando ventas y detalle de ventas...")
    t0 = time.time()
    cursor = conexion.cursor()

    df_ventas = df[df["y"] > 0].copy()
    df_diario = df_ventas.groupby(["date", "store_id"]).agg(
        items=("item_id", list),
        cantidades=("y", list),
        precios=("price", list)
    ).reset_index()

    contador_ventas = 0
    contador_detalles = 0
    tamano_lote = 500

    lotes_ventas = []
    detalles_por_venta = []

    for _, fila in df_diario.iterrows():
        total_venta = 0.0
        detalles = []

        for item_id, qty, price in zip(fila["items"], fila["cantidades"], fila["precios"]):
            if item_id in mapa_productos and qty > 0 and price > 0:
                subtotal = float(qty) * float(price)
                total_venta += subtotal
                detalles.append((
                    mapa_productos[item_id],
                    int(qty),
                    float(price),
                    round(subtotal, 2)
                ))

        if total_venta > 0:
            fecha = fila["date"]
            if isinstance(fecha, str):
                fecha = pd.to_datetime(fecha).date()
            elif hasattr(fecha, "date"):
                fecha = fecha.date()

            lotes_ventas.append((USUARIO_ID, fecha, round(total_venta, 2)))
            detalles_por_venta.append(detalles)
            contador_ventas += 1

            if len(lotes_ventas) >= tamano_lote:
                cursor.executemany(
                    "INSERT INTO venta (id_usuario, fecha_venta, total) VALUES (%s, %s, %s)",
                    lotes_ventas
                )
                primer_id = cursor.lastrowid

                detalles_con_venta = []
                for i, (venta_base, dets) in enumerate(zip(range(primer_id, primer_id + len(lotes_ventas)), detalles_por_venta)):
                    for det in dets:
                        detalles_con_venta.append((venta_base, det[0], det[1], det[2], det[3]))

                if detalles_con_venta:
                    cursor.executemany(
                        "INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
                        detalles_con_venta
                    )
                    contador_detalles += len(detalles_con_venta)

                lotes_ventas = []
                detalles_por_venta = []

    if lotes_ventas:
        cursor.executemany(
            "INSERT INTO venta (id_usuario, fecha_venta, total) VALUES (%s, %s, %s)",
            lotes_ventas
        )
        primer_id = cursor.lastrowid
        detalles_restantes = []
        for i, (venta_base, dets) in enumerate(zip(range(primer_id, primer_id + len(lotes_ventas)), detalles_por_venta)):
            for det in dets:
                detalles_restantes.append((venta_base, det[0], det[1], det[2], det[3]))

        if detalles_restantes:
            cursor.executemany(
                "INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
                detalles_restantes
            )
            contador_detalles += len(detalles_restantes)

    conexion.commit()
    cursor.close()
    print(f"  [OK] {contador_ventas:,} ventas insertadas")
    print(f"  [OK] {contador_detalles:,} detalles insertados")
    print(f"  Tiempo: {time.time() - t0:.1f}s")


def insertar_movimientos(conexion, df, mapa_productos):
    print("\n[8/8] Insertando movimientos de inventario...")
    t0 = time.time()
    cursor = conexion.cursor()

    lote = []
    tamano_lote = 1000

    for item_id, prod_id in mapa_productos.items():
        datos_item = df[(df["item_id"] == item_id) & (df["y"] > 0)].sort_values("date")

        stock_acumulado = 0
        for _, fila in datos_item.head(1).iterrows():
            cantidad = int(fila["y"]) * 3
            fecha = fila["date"]
            if hasattr(fecha, "to_pydatetime"):
                fecha = fecha.to_pydatetime()
            lote.append((prod_id, "ENTRADA", cantidad, fecha, "Reabastecimiento inicial"))
            stock_acumulado = cantidad

        for _, fila in datos_item.iterrows():
            cantidad = int(fila["y"])
            fecha = fila["date"]
            if hasattr(fecha, "to_pydatetime"):
                fecha = fecha.to_pydatetime()

            lote.append((prod_id, "SALIDA", cantidad, fecha, "Venta registrada"))
            stock_acumulado -= cantidad

            if stock_acumulado < 20:
                reposicion = cantidad * 3
                lote.append((prod_id, "ENTRADA", reposicion, fecha, "Reabastecimiento automatico"))
                stock_acumulado += reposicion

            if len(lote) >= tamano_lote:
                cursor.executemany(
                    """INSERT INTO movimiento_inventario (id_producto, tipo_movimiento, cantidad, fecha_movimiento, observacion)
                       VALUES (%s, %s, %s, %s, %s)""",
                    lote
                )
                lote = []

    if lote:
        cursor.executemany(
            """INSERT INTO movimiento_inventario (id_producto, tipo_movimiento, cantidad, fecha_movimiento, observacion)
               VALUES (%s, %s, %s, %s, %s)""",
            lote
        )

    conexion.commit()
    cursor.close()
    print(f"  Movimientos insertados en {time.time() - t0:.1f}s")


def insertar_metadata(conexion, df):
    print("\n[8/8] Insertando metadata de dataset y modelos...")
    cursor = conexion.cursor()

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

    conexion.commit()
    cursor.close()


def main():
    print("=" * 60)
    print("POBLAR BASE DE DATOS - DATOS M5")
    print("=" * 60)

    print("\nCargando dataset...")
    df = pd.read_csv(DIRECTORIO_PROCESADO / "m5_largo.csv")
    print(f"  Filas: {df.shape[0]:,}")
    print(f"  Productos unicos: {df['item_id'].nunique()}")
    print(f"  Tiendas: {df['store_id'].unique().tolist()}")

    productos_unicos = df.groupby("item_id").agg(
        demanda_total=("y", "sum"),
        cat_id=("cat_id", "first"),
        dept_id=("dept_id", "first"),
        price=("price", "mean")
    ).reset_index().sort_values("demanda_total", ascending=False)

    conexion = obtener_conexion()
    try:
        vaciar_tablas(conexion)
        id_categoria = insertar_categoria(conexion)
        ids_subcategorias = insertar_subcategorias(conexion, id_categoria)
        ids_proveedores = insertar_proveedores(conexion)
        id_usuario = insertar_usuario_defecto(conexion)
        mapa_productos = insertar_productos(conexion, productos_unicos, id_categoria, ids_subcategorias, ids_proveedores)
        insertar_inventarios(conexion, mapa_productos, df)
        insertar_ventas_y_detalle(conexion, df, mapa_productos)
        insertar_movimientos(conexion, df, mapa_productos)
        insertar_metadata(conexion, df)

        print("\n" + "=" * 60)
        print("BASE DE DATOS POBLADA EXITOSAMENTE!")
        print("=" * 60)
        print(f"  Categoria: {CATEGORIA_PRINCIPAL}")
        print(f"  Subcategorias: {len(ids_subcategorias)}")
        print(f"  Proveedores: {len(ids_proveedores)}")
        print(f"  Productos: {len(mapa_productos)}")
        print(f"  Conexion: {DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['name']}")
    finally:
        conexion.close()


if __name__ == "__main__":
    main()
