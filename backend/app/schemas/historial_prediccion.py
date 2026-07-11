from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class HistorialPrediccionResponse(BaseModel):
    id_historial: int
    id_producto: int
    id_modelo: int
    fecha_prediccion: Optional[date]
    periodo: Optional[str]
    demanda_estimada: int
    confianza_min: Optional[float]
    confianza_max: Optional[float]
    horizonte_dias: Optional[int]
    porcentaje_confianza: Optional[float]
    fecha_archivado: Optional[datetime]
    motivo: Optional[str]
    nombre_producto: Optional[str] = None
    codigo_producto: Optional[str] = None
    nombre_modelo: Optional[str] = None
    nombre_subcategoria: Optional[str] = None
    nombre_categoria: Optional[str] = None

    class Config:
        from_attributes = True


class HistorialPrediccionListResponse(BaseModel):
    total: int
    registros: List[HistorialPrediccionResponse]
