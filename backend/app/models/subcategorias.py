from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Subcategoria(Base):
    __tablename__ = "subcategorias"

    id_subcategoria = Column(Integer, primary_key=True, autoincrement=True)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)

    categoria = relationship("Categoria", back_populates="subcategorias")
