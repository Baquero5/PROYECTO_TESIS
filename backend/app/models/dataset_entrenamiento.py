from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.sql import func
from app.core.database import Base


class DatasetEntrenamiento(Base):
    __tablename__ = "dataset_entrenamiento"

    id_dataset = Column(Integer, primary_key=True, autoincrement=True)
    nombre_dataset = Column(String(150), nullable=False)
    fecha_generacion = Column(Date, server_default=func.now())
    registros = Column(Integer, default=0)
    descripcion = Column(Text, nullable=True)
