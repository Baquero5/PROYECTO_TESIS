from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Reabastecimiento(Base):
    __tablename__ = "reabastecimiento"

    id_reabastecimiento = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    id_prediccion = Column(Integer, ForeignKey("prediccion.id_prediccion"), nullable=True)
    fecha_generacion = Column(Date, server_default=func.now())
    cantidad_sugerida = Column(Integer, default=0)
    estado = Column(String(30), default="PENDIENTE")
