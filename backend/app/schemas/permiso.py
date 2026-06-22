from pydantic import BaseModel
from typing import Optional, List


class PermisoCreate(BaseModel):
    codigo: str
    descripcion: Optional[str] = None


class PermisoUpdate(BaseModel):
    codigo: Optional[str] = None
    descripcion: Optional[str] = None


class PermisoResponse(BaseModel):
    id_permiso: int
    codigo: str
    descripcion: Optional[str]

    class Config:
        from_attributes = True


class RolPermisoCreate(BaseModel):
    id_permisos: List[int]


class RolPermisoResponse(BaseModel):
    id_rol: int
    id_permiso: int

    class Config:
        from_attributes = True
