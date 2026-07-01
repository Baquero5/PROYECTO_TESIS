from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime


class ModeloIACreate(BaseModel):
    id_dataset: int
    algoritmo: str = Field(..., min_length=1, max_length=100)
    version: Optional[str] = Field(None, max_length=50)


class ModeloIAUpdate(BaseModel):
    mae: Optional[float] = Field(None, ge=0)
    rmse: Optional[float] = Field(None, ge=0)
    mape: Optional[float] = Field(None, ge=0, le=100)
    r2: Optional[float] = Field(None, ge=0, le=1)
    archivo_modelo: Optional[str] = Field(None, max_length=300)
    parametros: Optional[str] = Field(None, max_length=1000)
    estado: Optional[Literal["ACTIVO", "INACTIVO"]] = None


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
