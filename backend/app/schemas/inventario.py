from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InventarioCreate(BaseModel):
    id_producto: int
    stock_actual: int = 0
    stock_minimo: int = 0
    stock_maximo: int = 0


class InventarioUpdate(BaseModel):
    stock_actual: Optional[int] = None
    stock_minimo: Optional[int] = None
    stock_maximo: Optional[int] = None


class InventarioResponse(BaseModel):
    id_inventario: int
    id_producto: int
    stock_actual: int
    stock_minimo: int
    stock_maximo: int
    ultima_actualizacion: Optional[datetime]

    class Config:
        from_attributes = True


class StockUpdate(BaseModel):
    cantidad: int
    tipo: str  # ENTRADA o SALIDA
    observacion: Optional[str] = None
