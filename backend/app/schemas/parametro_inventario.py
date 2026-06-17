from pydantic import BaseModel
from typing import Optional


class ParametroInventarioCreate(BaseModel):
    id_producto: int
    costo_orden: float = 0.0
    costo_mantenimiento: float = 0.0
    lead_time_dias: int = 0
    stock_seguridad: int = 0
    punto_reorden: int = 0
    eoq: int = 0


class ParametroInventarioUpdate(BaseModel):
    costo_orden: Optional[float] = None
    costo_mantenimiento: Optional[float] = None
    lead_time_dias: Optional[int] = None
    stock_seguridad: Optional[int] = None
    punto_reorden: Optional[int] = None
    eoq: Optional[int] = None


class ParametroInventarioResponse(BaseModel):
    id_parametro: int
    id_producto: int
    costo_orden: float
    costo_mantenimiento: float
    lead_time_dias: int
    stock_seguridad: int
    punto_reorden: int
    eoq: int

    class Config:
        from_attributes = True
