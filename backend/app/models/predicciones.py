from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Prediccion(Base):
    __tablename__ = "predicciones"

    id_prediccion = Column(Integer, primary_key=True, autoincrement=True)
    id_modelo = Column(Integer, ForeignKey("modelos_ia.id_modelo"), nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    fecha_prediccion = Column(Date, server_default=func.now())
    periodo = Column(String(20), nullable=True)
    demanda_estimada = Column(Integer, default=0)
