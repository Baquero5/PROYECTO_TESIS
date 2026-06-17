from pydantic import BaseModel
from typing import Optional


class RolCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class RolUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class RolResponse(BaseModel):
    id_rol: int
    nombre: str
    descripcion: Optional[str]

    class Config:
        from_attributes = True
