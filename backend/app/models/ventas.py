from sqlalchemy import Column, Integer, Date, Numeric, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Venta(Base):
    __tablename__ = "ventas"

    id_venta = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_tienda = Column(Integer, ForeignKey("tiendas.id_tienda"), nullable=True)
    fecha_venta = Column(Date, server_default=func.now())
    total = Column(Numeric(12, 2), default=0.0)
