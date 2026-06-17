from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MovimientoInventarioCreate(BaseModel):
    id_producto: int
    tipo_movimiento: str
    cantidad: int
    observacion: Optional[str] = None


class MovimientoInventarioResponse(BaseModel):
    id_movimiento: int
    id_producto: int
    tipo_movimiento: str
    cantidad: int
    fecha_movimiento: Optional[datetime]
    observacion: Optional[str]

    class Config:
        from_attributes = True
