from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base


class RolPermiso(Base):
    __tablename__ = "rol_permisos"

    id_rol = Column(Integer, ForeignKey("roles.id_rol"), primary_key=True)
    id_permiso = Column(Integer, ForeignKey("permisos.id_permiso"), primary_key=True)
