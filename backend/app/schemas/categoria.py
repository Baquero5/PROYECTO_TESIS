from pydantic import BaseModel, Field
from typing import Optional


class CategoriaCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=300)


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=300)


class CategoriaResponse(BaseModel):
    id_categoria: int
    nombre: str
    descripcion: Optional[str]

    class Config:
        from_attributes = True
