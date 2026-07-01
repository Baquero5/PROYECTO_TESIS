from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime


class DetalleVentaCreate(BaseModel):
    id_producto: int
    cantidad: int = Field(..., ge=1)
    precio_unitario: float = Field(..., ge=0)


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
    detalles: List[DetalleVentaCreate] = Field(..., min_length=1)

    @field_validator('detalles')
    @classmethod
    def validate_detalles_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError('Debe agregar al menos un producto a la venta')
        return v


class VentaResponse(BaseModel):
    id_venta: int
    id_usuario: int
    fecha_venta: Optional[date]
    total: float
    detalles: Optional[List[DetalleVentaResponse]] = None

    class Config:
        from_attributes = True
