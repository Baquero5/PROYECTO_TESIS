from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Alerta(Base):
    __tablename__ = "alerta"

    id_alerta = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    tipo_alerta = Column(String(50), nullable=False)
    mensaje = Column(Text, nullable=True)
    fecha_alerta = Column(DateTime(timezone=True), server_default=func.now())
    estado = Column(String(20), default="ACTIVA")
    leida = Column(Boolean, default=False)
