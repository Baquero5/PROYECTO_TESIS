from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class Rol(Base):
    __tablename__ = "rol"

    id_rol = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
