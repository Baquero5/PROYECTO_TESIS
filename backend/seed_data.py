import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def seed_data():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login
        login_resp = await client.post(f"{BASE_URL}/api/auth/login", json={
            "correo": "admin@sistema.com",
            "password": "Admin123!"
        })
        if login_resp.status_code != 200:
            print("Login failed:", login_resp.text)
            return
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create Categorias
        categorias = [
            {"nombre": "Electronicos", "descripcion": "Dispositivos electronicos y gadgets"},
            {"nombre": "Alimentos", "descripcion": "Productos alimenticios y bebidas"},
            {"nombre": "Ropa", "descripcion": "Vestimenta y accesorios"},
            {"nombre": "Hogar", "descripcion": "Articulos para el hogar"},
            {"nombre": "Deportes", "descripcion": "Equipamiento deportivo"},
        ]

        print("Creating categorias...")
        cat_ids = []
        for cat in categorias:
            resp = await client.post(f"{BASE_URL}/api/categorias", json=cat, headers=headers)
            if resp.status_code == 201:
                cat_ids.append(resp.json()["id_categoria"])
                print(f"  OK: {cat['nombre']}")
            elif resp.status_code == 409:
                # Already exists, find it
                all_cats = (await client.get(f"{BASE_URL}/api/categorias", headers=headers)).json()
                existing = next((c for c in all_cats if c["nombre"] == cat["nombre"]), None)
                if existing:
                    cat_ids.append(existing["id_categoria"])
                    print(f"  SKIP: {cat['nombre']} (already exists, id={existing['id_categoria']})")
                else:
                    print(f"  FAIL: {cat['nombre']}: {resp.text}")
            else:
                print(f"  FAIL: {cat['nombre']}: {resp.status_code} {resp.text}")

        if not cat_ids:
            print("No categorias available, aborting.")
            return

        # 2. Create Proveedores
        proveedores = [
            {"razon_social": "Distribuidora ABC", "ruc": "1792345678001", "telefono": "0991234567", "correo": "abc@distribuidora.com", "direccion": "Av. Principal 123"},
            {"razon_social": "Importaciones XYZ", "ruc": "1798765432001", "telefono": "0997654321", "correo": "xyz@importaciones.com", "direccion": "Calle Comercio 456"},
            {"razon_social": "Mayorista Central", "ruc": "1791122334001", "telefono": "0991122334", "correo": "contacto@mayorista.com", "direccion": "Av. Industrial 789"},
        ]

        print("\nCreating proveedores...")
        prov_ids = []
        for prov in proveedores:
            resp = await client.post(f"{BASE_URL}/api/proveedores", json=prov, headers=headers)
            if resp.status_code == 201:
                prov_ids.append(resp.json()["id_proveedor"])
                print(f"  OK: {prov['razon_social']}")
            elif resp.status_code == 400:
                all_provs = (await client.get(f"{BASE_URL}/api/proveedores", headers=headers)).json()
                existing = next((p for p in all_provs if p["ruc"] == prov["ruc"]), None)
                if existing:
                    prov_ids.append(existing["id_proveedor"])
                    print(f"  SKIP: {prov['razon_social']} (already exists, id={existing['id_proveedor']})")
                else:
                    print(f"  FAIL: {prov['razon_social']}: {resp.text}")
            else:
                print(f"  FAIL: {prov['razon_social']}: {resp.status_code} {resp.text}")

        if not prov_ids:
            print("No proveedores available, aborting.")
            return

        # Ensure we have enough category and provider IDs
        while len(cat_ids) < 3:
            cat_ids.append(cat_ids[0])
        while len(prov_ids) < 3:
            prov_ids.append(prov_ids[0])

        # 3. Create Productos
        productos = [
            {"id_categoria": cat_ids[0], "id_proveedor": prov_ids[0], "codigo": "ELEC-001", "nombre": "Laptop HP 15", "descripcion": "Laptop HP 15 pulgadas 8GB RAM", "precio_compra": 450.00, "precio_venta": 650.00},
            {"id_categoria": cat_ids[0], "id_proveedor": prov_ids[0], "codigo": "ELEC-002", "nombre": "Mouse Inalambrico", "descripcion": "Mouse wireless ergonomico", "precio_compra": 8.00, "precio_venta": 15.00},
            {"id_categoria": cat_ids[1], "id_proveedor": prov_ids[2], "codigo": "ALIM-001", "nombre": "Arroz 1kg", "descripcion": "Arroz grano largo", "precio_compra": 1.20, "precio_venta": 1.80},
            {"id_categoria": cat_ids[1], "id_proveedor": prov_ids[2], "codigo": "ALIM-002", "nombre": "Aceite Vegetal 1L", "descripcion": "Aceite de soya refinado", "precio_compra": 2.50, "precio_venta": 3.50},
            {"id_categoria": cat_ids[2], "id_proveedor": prov_ids[1], "codigo": "ROPA-001", "nombre": "Camiseta Basica", "descripcion": "Camiseta 100% algodon", "precio_compra": 5.00, "precio_venta": 12.00},
        ]

        print("\nCreating productos...")
        prod_ids = []
        for prod in productos:
            resp = await client.post(f"{BASE_URL}/api/products", json=prod, headers=headers)
            if resp.status_code == 201:
                prod_ids.append(resp.json()["id_producto"])
                print(f"  OK: {prod['nombre']}")
            elif resp.status_code == 400:
                all_prods = (await client.get(f"{BASE_URL}/api/products", headers=headers)).json()
                existing = next((p for p in all_prods if p["codigo"] == prod["codigo"]), None)
                if existing:
                    prod_ids.append(existing["id_producto"])
                    print(f"  SKIP: {prod['nombre']} (already exists, id={existing['id_producto']})")
                else:
                    print(f"  FAIL: {prod['nombre']}: {resp.text}")
            else:
                print(f"  FAIL: {prod['nombre']}: {resp.status_code} {resp.text}")

        if not prod_ids:
            print("No products created, aborting inventario.")
            return

        # 4. Create Inventario
        inventario = [
            {"id_producto": prod_ids[0], "stock_actual": 25, "stock_minimo": 5, "stock_maximo": 50},
            {"id_producto": prod_ids[1], "stock_actual": 150, "stock_minimo": 20, "stock_maximo": 300},
        ]
        if len(prod_ids) > 2:
            inventario.append({"id_producto": prod_ids[2], "stock_actual": 500, "stock_minimo": 100, "stock_maximo": 1000})
        if len(prod_ids) > 3:
            inventario.append({"id_producto": prod_ids[3], "stock_actual": 200, "stock_minimo": 50, "stock_maximo": 400})
        if len(prod_ids) > 4:
            inventario.append({"id_producto": prod_ids[4], "stock_actual": 80, "stock_minimo": 15, "stock_maximo": 200})

        print("\nCreating inventario...")
        for inv in inventario:
            resp = await client.post(f"{BASE_URL}/api/inventario", json=inv, headers=headers)
            if resp.status_code == 201:
                print(f"  OK: Producto {inv['id_producto']}: {inv['stock_actual']} unidades")
            elif resp.status_code == 400:
                print(f"  SKIP: Producto {inv['id_producto']} (inventario ya existe)")
            else:
                print(f"  FAIL: {resp.status_code} {resp.text}")

        print("\nSeed data completed!")
        print("\nLogin credentials:")
        print("  Email: admin@sistema.com")
        print("  Password: Admin123!")

if __name__ == "__main__":
    asyncio.run(seed_data())
