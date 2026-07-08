from sqlalchemy import Column, Integer, Numeric, ForeignKey
from app.core.database import Base


class ParametroInventario(Base):
    __tablename__ = "parametro_inventario"

    id_parametro = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    costo_orden = Column(Numeric(10, 2), default=0.0)
    costo_mantenimiento = Column(Numeric(10, 2), default=0.0)
    lead_time_dias = Column(Integer, default=0)
    stock_seguridad = Column(Integer, default=0)
    punto_reorden = Column(Integer, default=0)
    eoq = Column(Integer, default=0)
