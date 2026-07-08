from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.database import engine, Base, AsyncSessionLocal
import os
from app.presentation.auth_routes import router as auth_router
from app.presentation.product_routes import router as product_router
from app.presentation.rol_routes import router as rol_router
from app.presentation.categoria_routes import router as categoria_router
from app.presentation.proveedor_routes import router as proveedor_router
from app.presentation.inventario_routes import router as inventario_router
from app.presentation.venta_routes import router as venta_router
from app.presentation.parametro_inventario_routes import router as parametro_router
from app.presentation.reabastecimiento_routes import router as reabastecimiento_router
from app.presentation.alerta_routes import router as alerta_router
from app.presentation.dataset_routes import router as dataset_router
from app.presentation.modelo_ia_routes import router as modelo_ia_router
from app.presentation.prediccion_routes import router as prediccion_router
from app.presentation.historial_prediccion_routes import router as historial_router
from app.presentation.permiso_routes import router as permiso_router
from app.models.usuarios import Usuario
from app.models.roles import Rol
from app.models.permisos import Permiso
from app.models.rol_permisos import RolPermiso
from app.models.categorias import Categoria
from app.models.proveedores import Proveedor
from app.models.productos import Producto
from app.models.inventarios import Inventario
from app.models.movimientos_inventario import MovimientoInventario
from app.models.ventas import Venta
from app.models.detalle_ventas import DetalleVenta
from app.models.parametros_inventario import ParametroInventario
from app.models.reabastecimiento import Reabastecimiento
from app.models.alertas import Alerta
from app.models.dataset_entrenamiento import DatasetEntrenamiento
from app.models.modelos_ia import ModeloIA
from app.models.predicciones import Prediccion
from app.models.historial_predicciones import HistorialPrediccion
from app.services.auth_service import hash_password

settings = get_settings()

# Permisos por defecto del sistema
DEFAULT_PERMISOS = [
    # Productos
    ("PRODUCTOS_CREAR", "Crear productos"),
    ("PRODUCTOS_LEER", "Ver productos"),
    ("PRODUCTOS_ACTUALIZAR", "Actualizar productos"),
    ("PRODUCTOS_ELIMINAR", "Eliminar productos"),
    # Categorías
    ("CATEGORIAS_CREAR", "Crear categorías"),
    ("CATEGORIAS_LEER", "Ver categorías"),
    ("CATEGORIAS_ACTUALIZAR", "Actualizar categorías"),
    ("CATEGORIAS_ELIMINAR", "Eliminar categorías"),
    # Proveedores
    ("PROVEEDORES_CREAR", "Crear proveedores"),
    ("PROVEEDORES_LEER", "Ver proveedores"),
    ("PROVEEDORES_ACTUALIZAR", "Actualizar proveedores"),
    ("PROVEEDORES_ELIMINAR", "Eliminar proveedores"),
    # Inventario
    ("INVENTARIO_CREAR", "Crear movimientos de inventario"),
    ("INVENTARIO_LEER", "Ver inventario"),
    ("INVENTARIO_ACTUALIZAR", "Actualizar inventario"),
    ("INVENTARIO_ELIMINAR", "Eliminar movimientos"),
    # Ventas
    ("VENTAS_CREAR", "Crear ventas"),
    ("VENTAS_LEER", "Ver ventas"),
    ("VENTAS_ACTUALIZAR", "Actualizar ventas"),
    ("VENTAS_ELIMINAR", "Eliminar ventas"),
    # Alertas
    ("ALERTAS_CREAR", "Crear alertas"),
    ("ALERTAS_LEER", "Ver alertas"),
    ("ALERTAS_ACTUALIZAR", "Actualizar alertas"),
    ("ALERTAS_ELIMINAR", "Eliminar alertas"),
    # Usuarios
    ("USUARIOS_CREAR", "Crear usuarios"),
    ("USUARIOS_LEER", "Ver usuarios"),
    ("USUARIOS_ACTUALIZAR", "Actualizar usuarios"),
    ("USUARIOS_ELIMINAR", "Eliminar usuarios"),
    # Roles
    ("ROLES_CREAR", "Crear roles"),
    ("ROLES_LEER", "Ver roles"),
    ("ROLES_ACTUALIZAR", "Actualizar roles"),
    ("ROLES_ELIMINAR", "Eliminar roles"),
    # Reportes
    ("REPORTES_LEER", "Ver reportes"),
    # Configuración
    ("CONFIGURACION_CREAR", "Crear configuración"),
    ("CONFIGURACION_LEER", "Ver configuración"),
    ("CONFIGURACION_ACTUALIZAR", "Actualizar configuración"),
    ("CONFIGURACION_ELIMINAR", "Eliminar configuración"),
    # Predicción IA
    ("PREDICCION_IA_LEER", "Ver predicciones IA"),
]

# Permisos por rol
ROLE_PERMISSIONS = {
    "ADMINISTRADOR": [p[0] for p in DEFAULT_PERMISOS],  # Todos los permisos
    "SISTEMAS": [
        "PRODUCTOS_CREAR", "PRODUCTOS_LEER", "PRODUCTOS_ACTUALIZAR", "PRODUCTOS_ELIMINAR",
        "CATEGORIAS_CREAR", "CATEGORIAS_LEER", "CATEGORIAS_ACTUALIZAR", "CATEGORIAS_ELIMINAR",
        "PROVEEDORES_CREAR", "PROVEEDORES_LEER", "PROVEEDORES_ACTUALIZAR", "PROVEEDORES_ELIMINAR",
        "INVENTARIO_CREAR", "INVENTARIO_LEER", "INVENTARIO_ACTUALIZAR", "INVENTARIO_ELIMINAR",
        "VENTAS_LEER",
        "ALERTAS_CREAR", "ALERTAS_LEER", "ALERTAS_ACTUALIZAR", "ALERTAS_ELIMINAR",
        "USUARIOS_LEER",
        "REPORTES_LEER",
        "CONFIGURACION_CREAR", "CONFIGURACION_LEER", "CONFIGURACION_ACTUALIZAR", "CONFIGURACION_ELIMINAR",
        "PREDICCION_IA_LEER",
    ],
    "VENTAS": [
        "PRODUCTOS_LEER",
        "CATEGORIAS_LEER",
        "PROVEEDORES_LEER",
        "INVENTARIO_LEER",
        "VENTAS_CREAR", "VENTAS_LEER", "VENTAS_ACTUALIZAR", "VENTAS_ELIMINAR",
        "ALERTAS_LEER",
        "REPORTES_LEER",
    ],
}


async def create_default_data():
    from sqlalchemy import select
    from app.models.rol_permisos import RolPermiso
    
    async with AsyncSessionLocal() as db:
        # Crear permisos
        for codigo, descripcion in DEFAULT_PERMISOS:
            result = await db.execute(select(Permiso).where(Permiso.codigo == codigo))
            if result.scalar_one_or_none() is None:
                permiso = Permiso(codigo=codigo, descripcion=descripcion)
                db.add(permiso)
        await db.commit()
        print(f"[OK] {len(DEFAULT_PERMISOS)} permisos creados")
        
        # Crear roles y asignar permisos
        for rol_nombre, permisos_codes in ROLE_PERMISSIONS.items():
            result = await db.execute(select(Rol).where(Rol.nombre == rol_nombre))
            rol = result.scalar_one_or_none()
            if rol is None:
                rol = Rol(nombre=rol_nombre, descripcion=f"Rol {rol_nombre}")
                db.add(rol)
                await db.flush()
            
            # Obtener IDs de permisos
            permiso_ids = []
            for code in permisos_codes:
                result = await db.execute(select(Permiso).where(Permiso.codigo == code))
                permiso = result.scalar_one_or_none()
                if permiso:
                    permiso_ids.append(permiso.id_permiso)
            
            # Asignar permisos al rol
            for permiso_id in permiso_ids:
                result = await db.execute(
                    select(RolPermiso).where(
                        RolPermiso.id_rol == rol.id_rol,
                        RolPermiso.id_permiso == permiso_id
                    )
                )
                if result.scalar_one_or_none() is None:
                    rol_permiso = RolPermiso(id_rol=rol.id_rol, id_permiso=permiso_id)
                    db.add(rol_permiso)
            
            await db.commit()
            print(f"[OK] Rol {rol_nombre} configurado con {len(permiso_ids)} permisos")


async def create_admin_user():
    from sqlalchemy import select
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Usuario).where(Usuario.correo == "admin@sistema.com"))
        if result.scalar_one_or_none() is None:
            admin_rol = await db.execute(select(Rol).where(Rol.nombre == "ADMINISTRADOR"))
            rol = admin_rol.scalar_one_or_none()
            if rol is None:
                rol = Rol(nombre="ADMINISTRADOR", descripcion="Administrador del sistema")
                db.add(rol)
                await db.flush()
            
            admin = Usuario(
                id_rol=rol.id_rol,
                nombres="Administrador",
                apellidos="del Sistema",
                correo="admin@sistema.com",
                password_hash=hash_password("Admin123!"),
                estado=True,
            )
            db.add(admin)
            await db.commit()
            print("[OK] Usuario administrador creado: admin@sistema.com")
        else:
            print("[INFO] Usuario administrador ya existe")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[START] Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    os.makedirs(settings.MODELS_PATH, exist_ok=True)
    print(f"[OK] Directorio de modelos: {settings.MODELS_PATH}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Tablas creadas en la base de datos")
    await create_default_data()
    await create_admin_user()
    yield
    print("[STOP] Apagando servidor...")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"],
)

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(rol_router)
app.include_router(categoria_router)
app.include_router(proveedor_router)
app.include_router(inventario_router)
app.include_router(venta_router)
app.include_router(parametro_router)
app.include_router(reabastecimiento_router)
app.include_router(alerta_router)
app.include_router(dataset_router)
app.include_router(modelo_ia_router)
app.include_router(prediccion_router)
app.include_router(historial_router)
app.include_router(permiso_router)


@app.get("/")
async def root():
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}
