from pydantic import BaseModel, Field
from typing import Optional


class SubcategoriaCreate(BaseModel):
    id_categoria: int
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=300)


class SubcategoriaUpdate(BaseModel):
    id_categoria: Optional[int] = None
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=300)


class SubcategoriaResponse(BaseModel):
    id_subcategoria: int
    id_categoria: int
    nombre: str
    descripcion: Optional[str]

    class Config:
        from_attributes = True
