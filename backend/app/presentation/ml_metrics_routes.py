from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.schemas.ml_metrics import (
    ModelMetric,
    FeatureImportanceResponse,
    ChartInfo,
    ComparativaResponse,
    AllMetricsResponse,
)
from app.services.ml_metrics_service import ml_metrics_service
from app.services.auth_service import require_permission
from typing import List

router = APIRouter(prefix="/api/ml-metrics", tags=["ML Metrics"])


@router.get("", response_model=AllMetricsResponse)
async def get_all_metrics(
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    """Retorna todas las métricas de modelos ML."""
    return ml_metrics_service.get_all_metrics()


@router.get("/comparativa", response_model=ComparativaResponse)
async def get_comparativa(
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    """Retorna métricas comparativas de modelos."""
    data = ml_metrics_service.get_comparativa()
    if not data:
        raise HTTPException(status_code=404, detail="No hay datos comparativos disponibles")
    return data


@router.get("/ensemble")
async def get_ensemble_metrics(
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    """Retorna métricas del modelo Ensemble."""
    data = ml_metrics_service.get_ensemble_metrics()
    if not data:
        raise HTTPException(status_code=404, detail="No hay métricas de Ensemble disponibles")
    return data


@router.get("/features", response_model=FeatureImportanceResponse)
async def get_feature_importance(
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    """Retorna datos de importancia de features."""
    data = ml_metrics_service.get_feature_importance_data()
    if not data:
        raise HTTPException(status_code=404, detail="No hay datos de importancia de features")
    return data


@router.get("/charts", response_model=List[ChartInfo])
async def get_available_charts(
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    """Retorna lista de gráficas disponibles."""
    return ml_metrics_service.get_available_charts()


@router.get("/charts/{chart_id}")
async def get_chart(chart_id: str, user=Depends(require_permission("PREDICCION_IA_LEER"))):
    """Retorna una gráfica por su ID."""
    chart_path = ml_metrics_service.get_chart_path(chart_id)
    if not chart_path:
        raise HTTPException(status_code=404, detail=f"Gráfica '{chart_id}' no encontrada")
    return FileResponse(chart_path, media_type="image/png")


@router.get("/summary", response_model=List[ModelMetric])
async def get_model_summary(user=Depends(require_permission("PREDICCION_IA_LEER"))):
    """Retorna resumen de modelos para tabla."""
    return ml_metrics_service.get_model_summary()


@router.get("/reporte")
async def get_reporte(user=Depends(require_permission("PREDICCION_IA_LEER"))):
    """Retorna reporte en texto plano."""
    reporte = ml_metrics_service.get_reporte_texto()
    if not reporte:
        raise HTTPException(status_code=404, detail="No hay reporte disponible")
    return {"reporte": reporte}
