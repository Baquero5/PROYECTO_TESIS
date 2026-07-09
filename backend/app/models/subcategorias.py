from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.core.database import Base


class Subcategoria(Base):
    __tablename__ = "subcategoria"

    id_subcategoria = Column(Integer, primary_key=True, autoincrement=True)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), nullable=False)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
