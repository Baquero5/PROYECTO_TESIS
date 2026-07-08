from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Inventario(Base):
    __tablename__ = "inventarios"

    id_inventario = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    id_tienda = Column(Integer, ForeignKey("tiendas.id_tienda"), nullable=True)
    stock_actual = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=0)
    stock_maximo = Column(Integer, default=0)
    ultima_actualizacion = Column(DateTime(timezone=True), server_default=func.now())

    tienda = relationship("Tienda", back_populates="inventarios")
