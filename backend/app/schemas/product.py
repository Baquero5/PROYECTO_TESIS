from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    id_categoria: int
    id_proveedor: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    precio_compra: float = 0.0
    precio_venta: float = 0.0


class ProductUpdate(BaseModel):
    id_categoria: Optional[int] = None
    id_proveedor: Optional[int] = None
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_compra: Optional[float] = None
    precio_venta: Optional[float] = None
    estado: Optional[bool] = None


class ProductResponse(BaseModel):
    id_producto: int
    id_categoria: int
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
