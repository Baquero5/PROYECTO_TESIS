from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AlertaCreate(BaseModel):
    id_producto: int
    tipo_alerta: str
    mensaje: Optional[str] = None


class AlertaUpdate(BaseModel):
    estado: Optional[str] = None
    mensaje: Optional[str] = None


class AlertaResponse(BaseModel):
    id_alerta: int
    id_producto: int
    tipo_alerta: str
    mensaje: Optional[str]
    fecha_alerta: Optional[datetime]
    estado: str

    class Config:
        from_attributes = True
