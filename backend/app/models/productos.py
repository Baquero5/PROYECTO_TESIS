from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Producto(Base):
    __tablename__ = "productos"

    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=False)
    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=False)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio_compra = Column(Numeric(10, 2), default=0.0)
    precio_venta = Column(Numeric(10, 2), default=0.0)
    estado = Column(Boolean, default=True)
    fecha_ingreso = Column(DateTime(timezone=True), server_default=func.now())
