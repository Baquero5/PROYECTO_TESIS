from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime


class InventarioCreate(BaseModel):
    id_producto: int
    stock_actual: int = Field(0, ge=0)
    stock_minimo: int = Field(0, ge=0)
    stock_maximo: int = Field(0, ge=0)

    @field_validator('stock_maximo')
    @classmethod
    def validate_max_vs_min(cls, v, info):
        minimo = info.data.get('stock_minimo')
        if minimo is not None and v > 0 and minimo >= v:
            raise ValueError('El stock máximo debe ser mayor que el mínimo')
        return v


class InventarioUpdate(BaseModel):
    stock_actual: Optional[int] = Field(None, ge=0)
    stock_minimo: Optional[int] = Field(None, ge=0)
    stock_maximo: Optional[int] = Field(None, ge=0)


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
    cantidad: int = Field(..., ge=1)
    tipo: Literal["ENTRADA", "SALIDA"]
    observacion: Optional[str] = Field(None, max_length=300)
