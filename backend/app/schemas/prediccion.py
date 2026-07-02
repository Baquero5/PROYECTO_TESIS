from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class PrediccionRequest(BaseModel):
    id_producto: int
    horizonte_dias: int = Field(default=30, ge=1, le=365)
    id_modelo: Optional[int] = None
    fecha_inicio: Optional[date] = None


class PrediccionBatchRequest(BaseModel):
    ids_productos: List[int]
    horizonte_dias: int = Field(default=30, ge=1, le=365)
    id_modelo: Optional[int] = None
    fecha_inicio: Optional[date] = None


class PrediccionCreate(BaseModel):
    id_modelo: int
    id_producto: int
    periodo: Optional[str] = None
    demanda_estimada: int = Field(default=0, ge=0)
    confianza_min: Optional[float] = None
    confianza_max: Optional[float] = None
    horizonte_dias: Optional[int] = Field(default=30, ge=1, le=365)
    porcentaje_confianza: Optional[float] = Field(default=95.0, ge=0, le=100)


class PrediccionResponse(BaseModel):
    id_prediccion: int
    id_modelo: int
    id_producto: int
    fecha_prediccion: Optional[date]
    periodo: Optional[str]
    demanda_estimada: int
    confianza_min: Optional[float]
    confianza_max: Optional[float]
    horizonte_dias: Optional[int]
    porcentaje_confianza: Optional[float]
    precio_venta: Optional[float] = None
    precio_compra: Optional[float] = None
    ingreso_esperado: Optional[float] = None
    ganancia_esperada: Optional[float] = None
    margen_porcentaje: Optional[float] = None

    class Config:
        from_attributes = True


class PrediccionBatchResponse(BaseModel):
    total_productos: int
    exitosos: int
    fallidos: int
    productos_exitosos: List[int]
    productos_fallidos: List[int]
    detalle_errores: List[str]


class KPIPrediccion(BaseModel):
    id_producto: int
    codigo: str
    nombre: str
    demanda_total: int
    demanda_minima: float
    demanda_maxima: float
    precio_venta: float
    precio_compra: float
    margen_unitario: float
    ingreso_esperado: float
    costo_esperado: float
    ganancia_esperada: float
    margen_porcentaje: float


class KPIsResponse(BaseModel):
    total_productos: int
    ingreso_total_esperado: float
    ganancia_total_esperada: float
    costo_total_esperado: float
    producto_mayor_volumen: Optional[KPIPrediccion]
    producto_mayor_rentabilidad: Optional[KPIPrediccion]
    producto_mayor_ingreso: Optional[KPIPrediccion]
    productos: List[KPIPrediccion]
