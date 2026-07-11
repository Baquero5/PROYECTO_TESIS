from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.historial_prediccion_repository import HistorialPrediccionRepository
from app.schemas.historial_prediccion import HistorialPrediccionResponse, HistorialPrediccionListResponse
from app.services.auth_service import require_permission
from typing import List

router = APIRouter(prefix="/api/historial-predicciones", tags=["Historial de Predicciones"])


@router.get("", response_model=HistorialPrediccionListResponse)
async def get_historial(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    repo = HistorialPrediccionRepository(db)
    total = await repo.get_count()
    registros = await repo.get_with_pagination(skip=skip, limit=limit)

    response = []
    for reg in registros:
        response.append(HistorialPrediccionResponse(
            id_historial=reg["id_historial"],
            id_producto=reg["id_producto"],
            id_modelo=reg["id_modelo"],
            fecha_prediccion=reg["fecha_prediccion"],
            periodo=reg["periodo"],
            demanda_estimada=reg["demanda_estimada"],
            confianza_min=float(reg["confianza_min"]) if reg["confianza_min"] else None,
            confianza_max=float(reg["confianza_max"]) if reg["confianza_max"] else None,
            horizonte_dias=reg["horizonte_dias"],
            porcentaje_confianza=float(reg["porcentaje_confianza"]) if reg["porcentaje_confianza"] else None,
            fecha_archivado=reg["fecha_archivado"],
            motivo=reg["motivo"],
            codigo_producto=reg["codigo_producto"],
            nombre_producto=reg["nombre_producto"],
            nombre_modelo=reg["nombre_modelo"],
            nombre_subcategoria=reg["nombre_subcategoria"],
            nombre_categoria=reg["nombre_categoria"],
        ))

    return HistorialPrediccionListResponse(total=total, registros=response)


@router.get("/producto/{producto_id}", response_model=List[HistorialPrediccionResponse])
async def get_historial_by_product(
    producto_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    repo = HistorialPrediccionRepository(db)
    registros = await repo.get_by_product(producto_id)

    response = []
    for reg in registros:
        response.append(HistorialPrediccionResponse(
            id_historial=reg.id_historial,
            id_producto=reg.id_producto,
            id_modelo=reg.id_modelo,
            fecha_prediccion=reg.fecha_prediccion,
            periodo=reg.periodo,
            demanda_estimada=reg.demanda_estimada,
            confianza_min=float(reg.confianza_min) if reg.confianza_min else None,
            confianza_max=float(reg.confianza_max) if reg.confianza_max else None,
            horizonte_dias=reg.horizonte_dias,
            porcentaje_confianza=float(reg.porcentaje_confianza) if reg.porcentaje_confianza else None,
            fecha_archivado=reg.fecha_archivado,
            motivo=reg.motivo,
        ))

    return response
