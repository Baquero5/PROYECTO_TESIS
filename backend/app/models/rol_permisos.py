from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base


class RolPermiso(Base):
    __tablename__ = "rol_permiso"

    id_rol = Column(Integer, ForeignKey("rol.id_rol"), primary_key=True)
    id_permiso = Column(Integer, ForeignKey("permiso.id_permiso"), primary_key=True)
