from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Tienda(Base):
    __tablename__ = "tiendas"

    id_tienda = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    ciudad = Column(String(100), nullable=False)
    estado = Column(String(50), nullable=False)
    region = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)

    inventarios = relationship("Inventario", back_populates="tienda")
