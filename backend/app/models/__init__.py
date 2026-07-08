# Modelos de seguridad
from app.models.roles import Rol
from app.models.usuarios import Usuario
from app.models.permisos import Permiso
from app.models.rol_permisos import RolPermiso

# Modelos de catálogo
from app.models.categorias import Categoria
from app.models.subcategorias import Subcategoria
from app.models.proveedores import Proveedor
from app.models.productos import Producto
from app.models.tiendas import Tienda

# Modelos de inventario
from app.models.inventarios import Inventario
from app.models.movimientos_inventario import MovimientoInventario

# Modelos comerciales
from app.models.ventas import Venta
from app.models.detalle_ventas import DetalleVenta

# Modelos de optimización de inventarios
from app.models.parametros_inventario import ParametroInventario
from app.models.alertas import Alerta

# Modelos de machine learning
from app.models.dataset_entrenamiento import DatasetEntrenamiento
from app.models.modelos_ia import ModeloIA
from app.models.predicciones import Prediccion
from app.models.historial_predicciones import HistorialPrediccion
from app.models.reabastecimiento import Reabastecimiento

__all__ = [
    "Rol",
    "Usuario",
    "Permiso",
    "RolPermiso",
    "Categoria",
    "Subcategoria",
    "Proveedor",
    "Producto",
    "Tienda",
    "Inventario",
    "MovimientoInventario",
    "Venta",
    "DetalleVenta",
    "ParametroInventario",
    "Alerta",
    "DatasetEntrenamiento",
    "ModeloIA",
    "Prediccion",
    "HistorialPrediccion",
    "Reabastecimiento",
]
