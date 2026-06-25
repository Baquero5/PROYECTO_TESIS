from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ModeloIACreate(BaseModel):
    id_dataset: int
    algoritmo: str
    version: Optional[str] = None


class ModeloIAUpdate(BaseModel):
    mae: Optional[float] = None
    rmse: Optional[float] = None
    mape: Optional[float] = None
    r2: Optional[float] = None
    archivo_modelo: Optional[str] = None
    parametros: Optional[str] = None
    estado: Optional[str] = None


class ModeloIAResponse(BaseModel):
    id_modelo: int
    id_dataset: int
    algoritmo: str
    version: Optional[str]
    mae: Optional[float]
    rmse: Optional[float]
    mape: Optional[float]
    r2: Optional[float]
    fecha_entrenamiento: Optional[datetime]
    archivo_modelo: Optional[str]
    parametros: Optional[str]
    estado: Optional[str]

    class Config:
        from_attributes = True
