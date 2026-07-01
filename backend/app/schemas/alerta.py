from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class AlertaCreate(BaseModel):
    id_producto: int
    tipo_alerta: Literal["PREVENTIVA", "CRITICA"]
    mensaje: Optional[str] = Field(None, max_length=500)


class AlertaUpdate(BaseModel):
    estado: Optional[Literal["ACTIVA", "RESUELTA"]] = None
    mensaje: Optional[str] = Field(None, max_length=500)
    leida: Optional[bool] = None


class AlertaResponse(BaseModel):
    id_alerta: int
    id_producto: int
    tipo_alerta: str
    mensaje: Optional[str]
    fecha_alerta: Optional[datetime]
    estado: str
    leida: bool = False

    class Config:
        from_attributes = True
