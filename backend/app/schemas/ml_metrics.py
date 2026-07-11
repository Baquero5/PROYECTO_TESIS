from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ModelMetric(BaseModel):
    name: str
    algorithm: str
    version: Optional[str] = None
    mae: Optional[float] = None
    rmse: Optional[float] = None
    r2: Optional[float] = None
    mape: Optional[float] = None
    features: Optional[int] = None
    weights: Optional[Dict[str, float]] = None


class FeatureImportance(BaseModel):
    feature: str
    importance: float


class FeatureImportanceResponse(BaseModel):
    features: List[FeatureImportance]
    total_features: int


class ChartInfo(BaseModel):
    id: str
    filename: str
    available: bool


class ComparativaResponse(BaseModel):
    xgboost: Optional[Dict[str, Any]] = None
    lightgbm: Optional[Dict[str, Any]] = None


class AllMetricsResponse(BaseModel):
    comparativa: Optional[Dict[str, Any]] = None
    xgboost: Optional[Dict[str, Any]] = None
    lightgbm: Optional[Dict[str, Any]] = None
    ensemble: Optional[Dict[str, Any]] = None
    reporte: Optional[str] = None
