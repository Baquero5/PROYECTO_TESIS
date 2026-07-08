from pydantic import BaseModel, Field
from typing import Optional


class TiendaCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    ciudad: str = Field(..., min_length=1, max_length=100)
    estado: str = Field(..., min_length=1, max_length=50)
    region: str = Field(..., min_length=1, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=300)


class TiendaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    ciudad: Optional[str] = Field(None, min_length=1, max_length=100)
    estado: Optional[str] = Field(None, min_length=1, max_length=50)
    region: Optional[str] = Field(None, min_length=1, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=300)


class TiendaResponse(BaseModel):
    id_tienda: int
    nombre: str
    ciudad: str
    estado: str
    region: str
    descripcion: Optional[str]

    class Config:
        from_attributes = True
