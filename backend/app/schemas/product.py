from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    id_categoria: int
    id_subcategoria: Optional[int] = None
    id_proveedor: int
    codigo: str = Field(..., min_length=1, max_length=50)
    nombre: str = Field(..., min_length=1, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio_compra: float = Field(0.0, ge=0)
    precio_venta: float = Field(0.0, ge=0)


class ProductUpdate(BaseModel):
    id_categoria: Optional[int] = None
    id_subcategoria: Optional[int] = None
    id_proveedor: Optional[int] = None
    codigo: Optional[str] = Field(None, min_length=1, max_length=50)
    nombre: Optional[str] = Field(None, min_length=1, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio_compra: Optional[float] = Field(None, ge=0)
    precio_venta: Optional[float] = Field(None, ge=0)
    estado: Optional[bool] = None


class ProductResponse(BaseModel):
    id_producto: int
    id_categoria: int
    id_subcategoria: Optional[int] = None
    id_proveedor: int
    codigo: str
    nombre: str
    descripcion: Optional[str]
    precio_compra: float
    precio_venta: float
    estado: bool
    fecha_ingreso: Optional[datetime] = None

    class Config:
        from_attributes = True
