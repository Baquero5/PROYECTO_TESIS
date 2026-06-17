from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class DetalleVentaCreate(BaseModel):
    id_producto: int
    cantidad: int
    precio_unitario: float


class DetalleVentaResponse(BaseModel):
    id_detalle: int
    id_venta: int
    id_producto: int
    cantidad: int
    precio_unitario: float
    subtotal: float

    class Config:
        from_attributes = True


class VentaCreate(BaseModel):
    id_usuario: int
    detalles: List[DetalleVentaCreate]


class VentaResponse(BaseModel):
    id_venta: int
    id_usuario: int
    fecha_venta: Optional[date]
    total: float
    detalles: Optional[List[DetalleVentaResponse]] = None

    class Config:
        from_attributes = True
