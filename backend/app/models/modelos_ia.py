from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class ModeloIA(Base):
    __tablename__ = "modelo_ia"

    id_modelo = Column(Integer, primary_key=True, autoincrement=True)
    id_dataset = Column(Integer, ForeignKey("dataset_entrenamiento.id_dataset"), nullable=False)
    algoritmo = Column(String(100), nullable=False)
    version = Column(String(50), nullable=True)
    mae = Column(Numeric(10, 4), nullable=True)
    rmse = Column(Numeric(10, 4), nullable=True)
    mape = Column(Numeric(10, 4), nullable=True)
    r2 = Column(Numeric(10, 4), nullable=True)
    fecha_entrenamiento = Column(DateTime(timezone=True), server_default=func.now())
    archivo_modelo = Column(String(500), nullable=True)
    parametros = Column(Text, nullable=True)
    estado = Column(String(20), default="INACTIVO")
