from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Inventario(Base):
    __tablename__ = "inventario"

    id_inventario = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    stock_actual = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=0)
    stock_maximo = Column(Integer, default=0)
    ultima_actualizacion = Column(DateTime(timezone=True), server_default=func.now())
