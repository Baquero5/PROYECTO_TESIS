from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class HistorialPrediccion(Base):
    __tablename__ = "historial_prediccion"

    id_historial = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    id_modelo = Column(Integer, ForeignKey("modelo_ia.id_modelo"), nullable=False)
    fecha_prediccion = Column(Date, nullable=True)
    periodo = Column(String(20), nullable=True)
    demanda_estimada = Column(Integer, default=0)
    confianza_min = Column(Numeric(10, 2), nullable=True)
    confianza_max = Column(Numeric(10, 2), nullable=True)
    horizonte_dias = Column(Integer, default=30)
    porcentaje_confianza = Column(Numeric(5, 2), default=95.0)
    fecha_archivado = Column(DateTime(timezone=True), server_default=func.now())
    motivo = Column(String(50), default="REEMPLAZADA")
