"""
Script 04: Poblar base de datos MariaDB con datos del M5
Entrada: data/processed/m5_largo.csv
 Conexion: root:123456@localhost:3307/tesis_inventario
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
TIENDAS = config["dataset"]["tiendas"]

CATEGORIAS_MAP = {
    "FOODS": {"nombre": "Alimentos", "descripcion": "Productos alimenticios y bebidas"},
    "HOUSEHOLD": {"nombre": "Hogar", "descripcion": "Articulos para el hogar y limpieza"},
    "HOBBIES": {"nombre": "Deportes", "descripcion": "Equipamiento deportivo y ocio"},
}

NOMBRES_FOODS = [
    "Leche Entera 1L", "Arroz Premium 5kg", "Aceite Vegetal 1L", "Pan Blanco 600g",
    "Azúcar Refinada 1kg", "Sal de Mar 500g", "Fideos Spaghetti 500g", "Atún en Lata 170g",
    "Café Molido 250g", "Cereal Integral 375g", "Galletas Digestivas 200g", "Jugo de Naranja 1L",
    "Yogurt Natural 200g", "Mantequilla 200g", "Queso Fresco 500g", "Huevos Docena",
    "Pollo Entero 1.5kg", "Carne Molida 500g", "Chorizo 300g", "Tocino 200g",
    "Sardinas en Lata 150g", "Salsa de Tomate 400g", "Mayonesa 250g", "Mostaza 200g",
    "Vinagre Blanco 500ml", "Harina de Trigo 1kg", "Avena Integral 500g", "Miel Purа 350g",
    "Mermelada Fresa 250g", "Te Negro 100 bolsas", "Chocolate en Polvo 400g",
    "Leche en Polvo 400g", "Crema de Leche 200ml", "Agua Mineral 1.5L", "Gaseosa Cola 2L",
    "Cerveza Artesanal 355ml", "Vino Tinto 750ml", "Sidra Natural 330ml", "Energizante 250ml",
    "Snack Papas 150g", "Mani Salado 200g", "Nueces Mix 150g", "Pasas 200g",
    "Duraznos en Almíbar 500g", "Maíz Dulce 300g", "Frijoles Negros 400g", "Lentejas 500g",
    "Garbanzos 400g", "Champiñones 200g", "Pimiento Morron 200g", "Aceitunas Verdes 250g",
    "Pepinillos 350g", "Sopa Instantanea 85g", "Caldo de Pollo 1L", "Achiote 100g",
    "Comino Molido 50g", "Pimienta Negra 50g", "Orégano Seco 30g", "Cebolla Deshidratada 50g",
    "Ajo en Polvo 50g", "Pimentón Dulce 50g", "Cúrcuma 50g", "Canela en Polvo 50g",
    "Vainilla Esencia 100ml", "Bicarbonato 500g", "levadura Seca 100g",
    "Aceite de Oliva 500ml", "Pasta de Tomate 200g", "Salsa de Soya 250ml",
    "Coco Rallado 200g", "Almendras 150g", "Semillas de Girasol 200g",
    "Pistachos 100g", "Cacahuates 250g", "Granola 375g", "Barrita de Cereal 6uds",
    "Muesli 500g", "Fruta Deshidratada 200g", "Banana Chips 100g",
    "Papa Frita 100g", "Palomitas de Maíz 100g", "Chicles 12uds", "Caramelo 200g",
    "Chocolate Negro 100g", "Chocolate con Leche 100g", "Galletas de Vainilla 150g",
    "Torta en Porción 120g", "Donas 6uds", "Pan Dulce 400g", "Croissant 4uds",
    "Empanadas Congeladas 6uds", "Pizza Congelada 400g", "Helado Vainilla 1L",
    "Helado Chocolate 1L", "Helado Fresa 1L", "Sorbete de Lima 500ml",
    "Hielo Bolsa 1kg", "Leche de Soya 1L", "Leche de Almendras 1L",
    "Jugo de Manzana 1L", "Jugo de Uva 1L", "Néctar de Durazno 1L",
    "Café Instantáneo 100g", "Café en Grano 250g", "Café Descafeinado 200g",
    "Té Verde 50 bolsas", "Té de Manzanilla 50 bolsas", "Infusión Frutas 25 bolsas",
    "Leche Condensada 397g", "Dulce de Leche 400g", "Mermelada de Durazno 250g",
    "Mermelada de Limón 250g", "Aceite de Coco 200ml", "Sirope de Arce 250ml",
    "Salsa BBQ 350ml", "Salsa Buffalo 250ml", "Ketchup 500ml",
    "Aderezo César 250ml", "Aderezo Ranch 250ml", "Aderezo Italiano 250ml",
    "Mayonesa Light 250g", "Mostaza Dijon 200g", "Wasabi 42g",
    "Salsa Teriyaki 250ml", "Salsa Inglesa 150ml", "Tabasco 60ml",
    "Pan Integral 600g", "Pan de Centeno 500g", "Pan de Molde 500g",
    "Tortillas de Maíz 10uds", "Tortillas de Trigo 10uds", "Arepa 12uds",
    "Pita Bread 6uds", "Pan de Ajo 200g", "Baguette 300g",
    "Croissant de Mantequilla 4uds", "Muffin de Arándanos 4uds",
    "Sándwich Preparado 200g", "Wrap de Pollo 180g", "Ensalada Cesar 250g",
    "Ensalada Mixta 200g", "Sopa de Tomate 500ml", "Sopa de Pollo 500ml",
    "Crema de Champiñones 500ml", "Puré de Papas 200g", "Guacamole 200g",
    "Hummus 200g", "Tzatziki 170g", "Pico de Gallo 250g",
    "Fruta Fresca Mix 500g", "Verduras Orgánicas 400g", "Brocoli Fresco 300g",
    "Espinaca Baby 150g", "Lechuga Romana 300g", "Tomate Cherry 250g",
    "Pepino Importado 2uds", "Zanahoria Baby 250g", "Champiñones Frescos 200g",
    "Ajo Fresco 3uds", "Cebolla Blanca 3uds", "Cebolla Morada 3uds",
    "Limones 4uds", "Naranjas 4uds", "Manzanas 4uds", "Plátanos 1kg",
    "Pera 4uds", "Uvas 500g", "Fresas 250g", "Arándanos 125g",
    "Mango 2uds", "Piña 1ud", "Sandía 1ud", "Melón 1ud",
    "Aguacate 2uds", "Limón Tahití 4uds", "Clementinas 4uds",
    "Carne de Res 1kg", "Costillas de Cerdo 1kg", "Pechuga de Pollo 1kg",
    "Muslo de Pollo 1kg", "Chuleta de Cerdo 500g", "Filete de Pescado 500g",
    "Camarones 500g", "Calamar 300g", "Pulpo 300g",
    "Salchicha 500g", "Mortadela 300g", "Jamón 300g",
    "Pepperoni 200g", "Tocino Ahumado 200g", "Panceta 300g",
    "Leche Descremada 1L", "Leche Semidescremada 1L", "Leche Deslactosada 1L",
    "Leche Avena 1L", "Leche Arroz 1L", "Kefir Natural 500ml",
    "Queso Parmesano 200g", "Queso Gouda 200g", "Queso Mozzarella 250g",
    "Queso Crema 200g", "Queso Ricotta 250g", "Queso Azul 150g",
    "Yogurt Griego 170g", "Yogurt de Fresa 170g", "Yogurt de Vainilla 170g",
    "Kumis 200ml", "Leche Cultivada 200ml",
    "Agua de Coco 330ml", "Té Helado Durazno 500ml", "Limonada Natural 1L",
    "Limonada de Jamaica 1L", "Agua Saborizada Lima 500ml", "Agua Saborizada Naranja 500ml",
    "Malta Negra 355ml", "Ginger Ale 355ml", "Tónica 355ml",
    "Bebida Isotónica 500ml", "Smoothie de Frutas 300ml", "Kombucha 330ml",
]

NOMBRES_HOUSEHOLD = [
    "Detergente Líquido 2L", "Jabón de Manos 500ml", "Pañales Talla M 30uds",
    "Papel Higiénico 12 rollos", "Bolsas de Basura 50uds", "Limpiador Multiusos 1L",
    "Esponjas 6 unidades", "Jabón en Barra 6uds", "Suavizante de Ropa 2L",
    "Desinfectante 500ml", "Velas Aromáticas 3uds", "Aceite Esencial 30ml",
    "Toallas de Papel 6 rollos", "Servilletas 200uds", "Film Transparente 300m",
    "Aluminio 300m", "Containers de Vidrio 3uds", "Tupperware 5uds",
    "Fregonas 3uds", "Guantes de Limpieza 2uds", "Escoba", "Recogedor",
    "Trapeador", "Jaladera", "Cubo para Limpieza 10L", "Mopa 3uds",
    "Limpiacristales 500ml", "Aerosol Multiusos 300ml", "Pastillas para WC 4uds",
    "Fragancia Ambiental 250ml", "Repelente de Insectos 400ml", "Catch de Insectos 2uds",
    "Trampa para Ratas", "Fosforos 200uds", "Encendedor 3uds", "Vela Blanca 6uds",
    "Cera para Muebles 500ml", "Brillamuebles 350ml", "Limpiador de Piso 1L",
    "Desengrasante 500ml", "Lejía 1L", "Cloro 1L", "Jabón en Polvo 1kg",
    "Suavizante Ropa 1L", "Quita Manchas 500ml", "Limpiador de Baño 750ml",
    "Gel Antibacterial 250ml", "Spray Desinfectante 400ml", "Alcohol 70% 1L",
    "Toallitas Húmedas 80uds", "Toallitas Desinfectantes 30uds",
    "Pañales Talla S 28uds", "Pañales Talla L 26uds", "Toallas Femeninas 24uds",
    "Cotonetes 200uds", "Algodón 100g", "Cepillo de Dientes",
    "Pasta Dental 100ml", "Enjuague Bucal 500ml", "Jabón Líquido 500ml",
    "Champú 400ml", "Acondicionador 400ml", "Gel de Baño 500ml",
    "Esponja Natural 2uds", "Banderín Decorativo", "Cuadro Decorativo",
    "Marco de Fotos", "Reloj de Pared", "Lámpara de Mesa",
    "Cortinas 2m", "Sábanas Queen", "Edredón Queen", "Almohadas 2uds",
    "Cobertor King", "Manta Polar", "Toalla Baño 4uds", "Toalla Cocina 6uds",
    "Delantal", "Mittens para Horno", "Mantel", "Servilletero",
    "Jarrón Decorativo", "Maceta Pequeña", "Maceta Grande", "Tierra para Plantas",
    "Fertilizante 1kg", "Regadera", "Tijeras de Jardín", "Guantes de Jardín",
    "Manguera 15m", "Aspiradora 1200W", "Plancha de Ropa", "Secadora de Pelo",
    "Licuadora 1.5L", "Tostadora 2slots", "Horno Eléctrico", "Olla Arrocera",
    "Freidora de Aire", "Hervidor Eléctrico", "Batidora", "Sandwichera",
    "Exprimidor Manual", "Reyenda de Cocina", "Set de Ollas 5uds",
    "Sartén Antiadherente", "Cuchillo Cocina Set 5uds", "Tabla para Cortar",
    "Colador", "Rallador", "Medidor de Cocina", "Basurero Cocina 10L",
    "Basurero Reciclaje 30L", "Cesto de Ropa", "Percha 10uds", "Tendedero",
    "Clips para Ropa 20uds", "Canasta de Lavado", "Jabón para Ropa 3kg",
    "Esponja Industrial 3uds", "Cepillo de Ropa", "Mancha Quita 500ml",
    "Bolsas al Vacío 10uds", "Empacadores de Alimentos 100uds",
    "Vela de Aromaterapia", "Difusor de Aromas", "Incienso 20uds",
    "Aceite para Difusor 100ml", "Purificador de Aire", "Humidificador 3L",
    "Termómetro Digital", "Despertador Digital", "Luz LED Repuesto",
    "Pilas AA 4uds", "Pilas AAA 4uds", "Cable USB-C 1m", "Cable Lightning 1m",
    "Cargador Inalámbrico", "Foco LED 9W", "Foco LED 12W",
    "Regleta 6tomas", "Extensión 5m", "Adaptador Universal",
    "Organizador de Closet", "Cajón Organizador 3niveles",
    "Estante Flotante", "Gancho de Puerta", "Toallero", "Jabonera",
    "Dispensador de Jabón", "Cepillo Inodoro", "Escobillón",
    "Bote de Basura Pequeño", "Bote de Basura Mediano",
    "Contenedor de Basura 60L", "Contenedor de Reciclaje 40L",
    "Bolsa de Basura 30L x50", "Bolsa de Basura 60L x30",
    "Film Alimentos 30cm", "Papel para Hornear 10m",
    "Bandeja para Horno", "Moldes para Horno 6uds",
    "Moldes para Pastel 3uds", "Moldes para Hielo",
    "Jarra Medidora 1L", "Cucharas Medidoras 4uds",
    "Espátula Silicona", "Pinza de Cocina", "Cucharón",
    "Espumadera", "Cucharón de Madera", "Tenedor Cocina",
    "Cucharón de Madera 2", "Tapa para Sartén", "Tapa para Olla",
    "Colador de Pastas", "Exprimidor de Limón", "Abrillantador de Platos",
    "Secador de Platos", "Jabonera de Cocina", "Portarrollos",
    "Dispensador de Papel", "Cesto de Basura Pedal 30L",
    "Bote de Basura con Tapadera", "Basura Orgánica 20L",
]

NOMBRES_HOBBIES = [
    "Baloncesto Pro", "Raqueta de Tenis", "Bicicleta Montaña", "Pelota de Fútbol",
    "Kit de Pesca", "Camping Tienda 4p", "Snorkel Set", "Parque Infantil",
    "Carrito de Golf", "Tabla de Surf", "Esquís Alpine", "Bastones Senderismo",
    "Raquetball Set", "Pelota de Volleyball", "Golf Joystick", "Bolsa de Boxeo",
    "Mancuernas 5kg", "Barra de Dominadas", "Banda Elástica Set",
    "Tapete de Yoga", "Pelota de Pilates", "Saltar Cuerda", "Chaleco Pesado",
    "Guantes de Boxeo", "Casco Ciclismo", "Protectores Rodilla",
    "Patines 4 ruedas", "Skateboard", "Hoverboard", "Scooter Adulto",
    "Bádminton Set", "Ping Pong Set 4p", "Ajedrez Madera", "Dominó Set",
    "Dardos Tablero", "Cromo Profesional", "Pelota de Béisbol",
    "Guante de Béisbol", "Bate de Aluminio", "Casco Béisbol",
    "Hockey Hielo Stick", "Puck de Hockey", "Masque Portero",
    "Pelota de Golf 12uds", "Kit Golf Viaje", "Carro Golf Manual",
    "Binoculars 10x50", "Brújula Digital", "Linterna LED Recargable",
    "Cuerda Escalada 30m", "Mosquetón Acero", "Arnes Seguridad",
    "Chaleco Salvavidas", "Remo Kayak", "Paddle Surf",
    "Kite Surf Vela", "Equipo Buceo", "Aletas Natación",
    "Gafas Natación", "Gorro Natación", "Tablón Flotación",
    "Pelota Acuática", "Noria Acuática", "Caña de Pescar",
    "Rueda de Pesca", "Kit de Anzuelos", "Red de Pesca",
    "Bolsa Térmica Deportiva", "Botella Deportiva 1L", "Shaker Proteína",
    "Cinturón Lumbar", "Muñequeras 2uds", "Bandana Deportiva",
    "Gafas Deportivas", "Gorra Running", "Zapatillas Running",
    "Camiseta Técnica", "Short Deportivo", "Medias Compresión",
    "Ropa Interior Térmica", "Chaqueta Impermeable", "Pantalón Trekking",
    "Botín Senderismo", "Sandalia Deportiva", "Crocs Classic",
    "Lona Camping", "Saco de Dormir 0°C", "Colchoneta Aislante",
    "Hammock Camping", "Linterna Cabeza", "Cuchillo Multiusos",
    "Brújula Analógica", "Kit Supervivencia", "Mochila 60L",
    "Mochila 30L", "Bolsa Hidratación 2L", "Paraguas Automático",
    "Gafas Sol Deportivas", "Protector Solar SPF50", "Repelente 250ml",
    "Termo 1L", "Cooler Portátil", "Silla Plegable",
    "Mesa Plegable", "Sombrilla Playa", "Carpa Familiar",
    "Linterna Solar", "Panel Solar Portátil", "Cargador Solar",
    "Radio FM/AM", "Altavoz Bluetooth", "Auriculares Running",
    "Reloj GPS Deportivo", "Pulsómetro Chest", "Pedómetro Digital",
    "Balón Medicine 5kg", "Kettlebell 8kg", "Barra Olímpica",
    "Disco Peso 5kg", "Banco Press", "Máquina Remo",
    "Elíptica Doméstica", "Bicicleta Estática", "Caminadora Plegable",
    "Kit Boxeo Completo", "Saco Boxeo 1.5m", "Speed Ball",
    "Espada Esgrima", "Estoque Esgrima", "Máscara Esgrima",
    "Arco Compuesto", "Flechas Carbono 12uds", "Diana Múltiple",
    "Carabina 4.5mm", "Pistola Aire Comprimido", "Munición 500uds",
    "Bola de Bowling", "Bolso Bowling", "Guante Bowling",
    "Colchoneta Gym", "Barra Yoga", "Bloque Yoga 2uds",
    "Correa Yoga", "Pelota Medicinal 3kg", "TRX Set Completo",
    "Soga Crossfit", "Kimono Karate", "Cinturón Karate",
    "Tabi Básico", "Yoga Mat Extra Largo",
]


def get_nombre_realista(cat_code, index):
    """Retorna un nombre descriptivo realista para el producto."""
    if cat_code == "FOODS":
        nombres = NOMBRES_FOODS
    elif cat_code == "HOUSEHOLD":
        nombres = NOMBRES_HOUSEHOLD
    elif cat_code == "HOBBIES":
        nombres = NOMBRES_HOBBIES
    else:
        return f"Producto {index+1}"

    return nombres[index % len(nombres)]


PROVEEDORES_TEMPLATE = [
    ("Distribuidora Walmart California", "0991234567001", "0991234567", "distribuidora_ca@walmart.com", "123 Main St, CA"),
    ("Distribuidora Walmart Texas", "0991234567002", "0991234568", "distribuidora_tx@walmart.com", "456 Oak Ave, TX"),
    ("Distribuidora Walmart Wisconsin", "0991234567003", "0991234569", "distribuidora_wi@walmart.com", "789 Pine Rd, WI"),
    ("Logistica Nacional CA", "0991234567004", "0991234570", "logistica_ca@nationwide.com", "321 Elm St, CA"),
    ("Logistica Nacional TX", "0991234567005", "0991234571", "logistica_tx@nationwide.com", "654 Maple Dr, TX"),
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
        "movimientos_inventario",
        "detalle_ventas",
        "ventas",
        "inventarios",
        "productos",
        "proveedores",
        "categorias",
        "parametros_inventario",
        "alertas",
        "predicciones",
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


def insert_categorias(conn):
    print("\n[2/8] Insertando categorias...")
    cursor = conn.cursor()
    cat_ids = {}
    for cat_id_m5, info in CATEGORIAS_MAP.items():
        cursor.execute(
            "INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)",
            (info["nombre"], info["descripcion"])
        )
        cat_ids[cat_id_m5] = cursor.lastrowid
        print(f"  [OK] {info['nombre']} (id={cursor.lastrowid})")
    conn.commit()
    cursor.close()
    return cat_ids


def insert_proveedores(conn):
    print("\n[3/8] Insertando proveedores...")
    cursor = conn.cursor()
    prov_ids = []
    for prov in PROVEEDORES_TEMPLATE:
        cursor.execute(
            "INSERT INTO proveedores (razon_social, ruc, telefono, correo, direccion) VALUES (%s, %s, %s, %s, %s)",
            prov
        )
        prov_ids.append(cursor.lastrowid)
        print(f"  [OK] {prov[0]} (id={cursor.lastrowid})")
    conn.commit()
    cursor.close()
    return prov_ids


def insert_productos(conn, df_items, cat_ids, prov_ids):
    print(f"\n[4/8] Insertando {len(df_items)} productos...")
    cursor = conn.cursor()
    prod_ids_map = {}

    unique_items = df_items.groupby("item_id").first().reset_index()

    for i, row in unique_items.iterrows():
        cat_code = row["cat_id"]
        cat_id = cat_ids.get(cat_code, list(cat_ids.values())[0])
        prov_id = prov_ids[i % len(prov_ids)]

        precio_venta = float(row.get("price", 5.0))
        if precio_venta <= 0:
            precio_venta = round(random.uniform(1.0, 50.0), 2)
        precio_compra = round(precio_venta * 0.6, 2)

        codigo = f"{cat_code[:3].upper()}-{i+1:04d}"
        nombre = get_nombre_realista(cat_code, i)

        cursor.execute(
            """INSERT INTO productos (id_categoria, id_proveedor, codigo, nombre, 
               descripcion, precio_compra, precio_venta, estado)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (cat_id, prov_id, codigo, nombre,
             f"Producto {nombre} de la tienda M5",
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
            """INSERT INTO inventarios (id_producto, stock_actual, stock_minimo, stock_maximo)
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
    detalles_por_venta = []  # Lista de listas: cada sublista tiene los detalles de una venta

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
                    "INSERT INTO ventas (id_usuario, fecha_venta, total) VALUES (%s, %s, %s)",
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
            "INSERT INTO ventas (id_usuario, fecha_venta, total) VALUES (%s, %s, %s)",
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
                    """INSERT INTO movimientos_inventario (id_producto, tipo_movimiento, cantidad, fecha_movimiento, observacion)
                       VALUES (%s, %s, %s, %s, %s)""",
                    batch
                )
                batch = []

    if batch:
        cursor.executemany(
            """INSERT INTO movimientos_inventario (id_producto, tipo_movimiento, cantidad, fecha_movimiento, observacion)
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

    cursor.execute(
        """INSERT INTO dataset_entrenamiento (nombre_dataset, registros, descripcion)
           VALUES (%s, %s, %s)""",
        (f"M5 Walmart - {len(TIENDAS)} tiendas - {num_productos} productos",
         num_registros,
         f"Dataset M5 transformado. Tiendas: {', '.join(TIENDAS)}. {num_productos} productos top por demanda.")
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

    print("\nCargando dataset...")
    df = pd.read_csv(PROC_DIR / "m5_largo.csv")
    print(f"  Filas: {df.shape[0]:,}")
    print(f"  Productos unicos: {df['item_id'].nunique()}")
    print(f"  Tiendas: {df['store_id'].unique().tolist()}")

    unique_items = df.groupby("item_id").agg(
        total_demand=("y", "sum"),
        cat_id=("cat_id", "first")
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
