from pydantic import BaseModel
from typing import Optional
from datetime import date


class DatasetCreate(BaseModel):
    nombre_dataset: str
    registros: int = 0
    descripcion: Optional[str] = None


class DatasetUpdate(BaseModel):
    nombre_dataset: Optional[str] = None
    registros: Optional[int] = None
    descripcion: Optional[str] = None


class DatasetResponse(BaseModel):
    id_dataset: int
    nombre_dataset: str
    fecha_generacion: Optional[date]
    registros: int
    descripcion: Optional[str]

    class Config:
        from_attributes = True
