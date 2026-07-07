from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
