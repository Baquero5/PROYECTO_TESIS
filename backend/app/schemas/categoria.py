from pydantic import BaseModel
from typing import Optional


class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class CategoriaResponse(BaseModel):
    id_categoria: int
    nombre: str
    descripcion: Optional[str]

    class Config:
        from_attributes = True
