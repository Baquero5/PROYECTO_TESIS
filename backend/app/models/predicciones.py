from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
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
    confianza_min = Column(Numeric(10, 2), nullable=True)
    confianza_max = Column(Numeric(10, 2), nullable=True)
    horizonte_dias = Column(Integer, default=30)
    porcentaje_confianza = Column(Numeric(5, 2), default=95.0)
