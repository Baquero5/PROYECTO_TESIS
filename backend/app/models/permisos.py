from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class Permiso(Base):
    __tablename__ = "permisos"

    id_permiso = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    descripcion = Column(Text, nullable=True)
