from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.repositories.prediccion_repository import PrediccionRepository
from app.repositories.modelo_ia_repository import ModeloIARepository
from app.schemas.prediccion import PrediccionCreate, PrediccionResponse, PrediccionRequest, PrediccionBatchRequest, PrediccionBatchResponse
from app.services.ml_service import ml_service
from app.models.predicciones import Prediccion
from typing import List
import pandas as pd
from datetime import datetime

router = APIRouter(prefix="/api/predicciones", tags=["Predicciones"])


@router.get("", response_model=List[PrediccionResponse])
async def get_predicciones(db: AsyncSession = Depends(get_db)):
    repo = PrediccionRepository(db)
    return await repo.get_all()


@router.get("/{prediccion_id}", response_model=PrediccionResponse)
async def get_prediccion(prediccion_id: int, db: AsyncSession = Depends(get_db)):
    repo = PrediccionRepository(db)
    prediccion = await repo.get_by_id(prediccion_id)
    if not prediccion:
        raise HTTPException(status_code=404, detail="Predicción no encontrada")
    return prediccion


@router.get("/producto/{producto_id}", response_model=List[PrediccionResponse])
async def get_predicciones_by_product(producto_id: int, db: AsyncSession = Depends(get_db)):
    repo = PrediccionRepository(db)
    return await repo.get_by_product(producto_id)


@router.get("/producto/{producto_id}/ultima", response_model=PrediccionResponse)
async def get_latest_prediccion(producto_id: int, db: AsyncSession = Depends(get_db)):
    repo = PrediccionRepository(db)
    prediccion = await repo.get_latest(producto_id)
    if not prediccion:
        raise HTTPException(status_code=404, detail="No hay predicciones para este producto")
    return prediccion


@router.post("", response_model=PrediccionResponse, status_code=201)
async def create_prediccion(data: PrediccionCreate, db: AsyncSession = Depends(get_db)):
    repo = PrediccionRepository(db)
    prediccion = Prediccion(**data.model_dump())
    return await repo.create(prediccion)


@router.post("/predecir", response_model=List[PrediccionResponse], status_code=201)
async def predecir_demanda(data: PrediccionRequest, db: AsyncSession = Depends(get_db)):
    """Genera predicciones de demanda usando el modelo ML seleccionado o el activo."""
    modelo_repo = ModeloIARepository(db)
    
    if data.id_modelo:
        modelo = await modelo_repo.get_by_id(data.id_modelo)
    else:
        modelo = await modelo_repo.get_active()

    if not modelo or not modelo.archivo_modelo:
        raise HTTPException(
            status_code=404,
            detail="No hay modelo entrenado disponible. Entrene un modelo primero."
        )

    try:
        model = ml_service.load_model(modelo.archivo_modelo)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Archivo de modelo no encontrado: {modelo.archivo_modelo}"
        )

    result = await db.execute(
        text("""
            SELECT v.fecha_venta, dv.cantidad, dv.precio_unitario
            FROM detalle_ventas dv
            JOIN ventas v ON dv.id_venta = v.id_venta
            WHERE dv.id_producto = :producto_id
            ORDER BY v.fecha_venta ASC
        """),
        {"producto_id": data.id_producto}
    )
    rows = result.fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No hay historial de ventas para el producto {data.id_producto}"
        )

    historial_df = pd.DataFrame(rows, columns=["fecha_venta", "cantidad", "precio_unitario"])

    features_df = ml_service.prepare_features_from_history(historial_df)

    if len(features_df) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Se necesitan al menos 30 días de historial. Hay {len(features_df)} días disponibles."
        )

    predicciones_raw = ml_service.predict_demand(model, features_df, data.horizonte_dias)

    repo = PrediccionRepository(db)

    predicciones_obj = [
        Prediccion(
            id_modelo=modelo.id_modelo,
            id_producto=data.id_producto,
            fecha_prediccion=datetime.strptime(pred["fecha"], "%Y-%m-%d").date(),
            periodo=pred["fecha"][:7],
            demanda_estimada=pred["demanda_estimada"],
            confianza_min=pred["confianza_min"],
            confianza_max=pred["confianza_max"],
            horizonte_dias=data.horizonte_dias,
            porcentaje_confianza=95.0,
        )
        for pred in predicciones_raw
    ]

    predicciones_creadas = await repo.create_many(predicciones_obj)
    return predicciones_creadas


@router.post("/predecir-lote", response_model=PrediccionBatchResponse)
async def predecir_lote(data: PrediccionBatchRequest, db: AsyncSession = Depends(get_db)):
    """Genera predicciones para múltiples productos de una vez."""
    modelo_repo = ModeloIARepository(db)
    
    if data.id_modelo:
        modelo = await modelo_repo.get_by_id(data.id_modelo)
    else:
        modelo = await modelo_repo.get_active()

    if not modelo or not modelo.archivo_modelo:
        raise HTTPException(
            status_code=404,
            detail="No hay modelo entrenado disponible. Entrene un modelo primero."
        )

    try:
        model = ml_service.load_model(modelo.archivo_modelo)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Archivo de modelo no encontrado: {modelo.archivo_modelo}"
        )

    repo = PrediccionRepository(db)
    exitosos = []
    fallidos = []
    errores = []

    for producto_id in data.ids_productos:
        try:
            result = await db.execute(
                text("""
                    SELECT v.fecha_venta, dv.cantidad, dv.precio_unitario
                    FROM detalle_ventas dv
                    JOIN ventas v ON dv.id_venta = v.id_venta
                    WHERE dv.id_producto = :producto_id
                    ORDER BY v.fecha_venta ASC
                """),
                {"producto_id": producto_id}
            )
            rows = result.fetchall()

            if not rows:
                fallidos.append(producto_id)
                errores.append(f"Producto {producto_id}: Sin historial de ventas")
                continue

            historial_df = pd.DataFrame(rows, columns=["fecha_venta", "cantidad", "precio_unitario"])
            features_df = ml_service.prepare_features_from_history(historial_df)

            if len(features_df) < 30:
                fallidos.append(producto_id)
                errores.append(f"Producto {producto_id}: Historial insuficiente ({len(features_df)} días)")
                continue

            predicciones_raw = ml_service.predict_demand(model, features_df, data.horizonte_dias)

            predicciones_obj = [
                Prediccion(
                    id_modelo=modelo.id_modelo,
                    id_producto=producto_id,
                    fecha_prediccion=datetime.strptime(pred["fecha"], "%Y-%m-%d").date(),
                    periodo=pred["fecha"][:7],
                    demanda_estimada=pred["demanda_estimada"],
                    confianza_min=pred["confianza_min"],
                    confianza_max=pred["confianza_max"],
                    horizonte_dias=data.horizonte_dias,
                    porcentaje_confianza=95.0,
                )
                for pred in predicciones_raw
            ]

            await repo.create_many(predicciones_obj)
            exitosos.append(producto_id)

        except Exception as e:
            fallidos.append(producto_id)
            errores.append(f"Producto {producto_id}: {str(e)}")

    return PrediccionBatchResponse(
        total_productos=len(data.ids_productos),
        exitosos=len(exitosos),
        fallidos=len(fallidos),
        productos_exitosos=exitosos,
        productos_fallidos=fallidos,
        detalle_errores=errores
    )
