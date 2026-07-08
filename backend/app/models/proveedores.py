from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class Proveedor(Base):
    __tablename__ = "proveedor"

    id_proveedor = Column(Integer, primary_key=True, autoincrement=True)
    razon_social = Column(String(150), nullable=False)
    ruc = Column(String(13), nullable=False, unique=True)
    telefono = Column(String(20), nullable=True)
    correo = Column(String(100), nullable=True)
    direccion = Column(Text, nullable=True)
