from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.repositories.prediccion_repository import PrediccionRepository
from app.repositories.historial_prediccion_repository import HistorialPrediccionRepository
from app.repositories.modelo_ia_repository import ModeloIARepository
from app.schemas.prediccion import PrediccionCreate, PrediccionResponse, PrediccionRequest, PrediccionBatchRequest, PrediccionBatchResponse, KPIsResponse, KPIPrediccion
from app.services.ml_service import ml_service
from app.services.auth_service import require_permission
from app.models.predicciones import Prediccion
from typing import List
import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial

# Thread pool para predicciones ML (no bloquea event loop)
_ml_executor = ThreadPoolExecutor(max_workers=4)

# Lock por producto para evitar race conditions
_product_locks = {}

router = APIRouter(prefix="/api/predicciones", tags=["Predicciones"])


@router.get("", response_model=List[PrediccionResponse])
async def get_predicciones(
    id_modelo: int = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    query = """
        SELECT 
            pr.id_prediccion, pr.id_modelo, pr.id_producto,
            pr.fecha_prediccion, pr.periodo, pr.demanda_estimada,
            pr.confianza_min, pr.confianza_max, pr.horizonte_dias,
            pr.porcentaje_confianza,
            p.precio_venta, p.precio_compra,
            ROUND(pr.demanda_estimada * p.precio_venta, 2) as ingreso_esperado,
            ROUND(pr.demanda_estimada * (p.precio_venta - p.precio_compra), 2) as ganancia_esperada,
            CASE WHEN p.precio_venta > 0 
                 THEN ROUND((p.precio_venta - p.precio_compra) / p.precio_venta * 100, 2)
                 ELSE 0 END as margen_porcentaje,
            CASE WHEN pr.horizonte_dias > 0 
                 THEN ROUND(pr.demanda_estimada * 1.0 / pr.horizonte_dias, 2)
                 ELSE 0 END as venta_promedio_por_dia
        FROM prediccion pr
        INNER JOIN producto p ON pr.id_producto = p.id_producto
    """
    params = {}
    if id_modelo:
        query += " WHERE pr.id_modelo = :id_modelo"
        params["id_modelo"] = id_modelo
    query += " ORDER BY pr.fecha_prediccion DESC"
    result = await db.execute(text(query), params)
    rows = result.fetchall()
    
    predicciones = []
    for row in rows:
        predicciones.append(PrediccionResponse(
            id_prediccion=row.id_prediccion,
            id_modelo=row.id_modelo,
            id_producto=row.id_producto,
            fecha_prediccion=row.fecha_prediccion,
            periodo=row.periodo,
            demanda_estimada=row.demanda_estimada,
            confianza_min=float(row.confianza_min) if row.confianza_min else None,
            confianza_max=float(row.confianza_max) if row.confianza_max else None,
            horizonte_dias=row.horizonte_dias,
            porcentaje_confianza=float(row.porcentaje_confianza) if row.porcentaje_confianza else None,
            precio_venta=float(row.precio_venta) if row.precio_venta else None,
            precio_compra=float(row.precio_compra) if row.precio_compra else None,
            ingreso_esperado=float(row.ingreso_esperado) if row.ingreso_esperado else None,
            ganancia_esperada=float(row.ganancia_esperada) if row.ganancia_esperada else None,
            margen_porcentaje=float(row.margen_porcentaje) if row.margen_porcentaje else None,
            venta_promedio_por_dia=float(row.venta_promedio_por_dia) if row.venta_promedio_por_dia else None,
        ))
    
    return predicciones


@router.get("/kpis", response_model=KPIsResponse)
async def get_kpis_prediccion(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    """
    Calcula KPIs de rentabilidad basados en las predicciones existentes.
    Retorna: ingreso esperado, ganancia esperada, productos más rentables.
    """
    result = await db.execute(
        text("""
            SELECT 
                p.id_producto,
                p.codigo,
                p.nombre,
                p.precio_venta,
                p.precio_compra,
                COALESCE(SUM(pred.demanda_estimada), 0) as demanda_total,
                COALESCE(SUM(pred.confianza_min), 0) as demanda_minima,
                COALESCE(SUM(pred.confianza_max), 0) as demanda_maxima
            FROM producto p
            INNER JOIN prediccion pred ON p.id_producto = pred.id_producto
            INNER JOIN modelo_ia m ON pred.id_modelo = m.id_modelo
            WHERE p.estado = 1 AND m.estado = 'ACTIVO'
            GROUP BY p.id_producto, p.codigo, p.nombre, p.precio_venta, p.precio_compra
            HAVING demanda_total > 0
            ORDER BY demanda_total DESC
        """)
    )
    rows = result.fetchall()
    
    productos_kpi = []
    ingreso_total = 0
    ganancia_total = 0
    costo_total = 0
    
    for row in rows:
        precio_venta = float(row.precio_venta or 0)
        precio_compra = float(row.precio_compra or 0)
        demanda = int(row.demanda_total)
        demanda_min = float(row.demanda_minima)
        demanda_max = float(row.demanda_maxima)
        
        margen_unitario = precio_venta - precio_compra
        margen_porcentaje = (margen_unitario / precio_venta * 100) if precio_venta > 0 else 0
        
        ingreso_esperado = demanda * precio_venta
        costo_esperado = demanda * precio_compra
        ganancia_esperada = demanda * margen_unitario
        
        ingreso_total += ingreso_esperado
        ganancia_total += ganancia_esperada
        costo_total += costo_esperado
        
        kpi = KPIPrediccion(
            id_producto=row.id_producto,
            codigo=row.codigo,
            nombre=row.nombre,
            demanda_total=demanda,
            demanda_minima=demanda_min,
            demanda_maxima=demanda_max,
            precio_venta=precio_venta,
            precio_compra=precio_compra,
            margen_unitario=margen_unitario,
            ingreso_esperado=ingreso_esperado,
            costo_esperado=costo_esperado,
            ganancia_esperada=ganancia_esperada,
            margen_porcentaje=round(margen_porcentaje, 2)
        )
        productos_kpi.append(kpi)
    
    producto_mayor_volumen = max(productos_kpi, key=lambda x: x.demanda_total) if productos_kpi else None
    producto_mayor_rentabilidad = max(productos_kpi, key=lambda x: x.ganancia_esperada) if productos_kpi else None
    producto_mayor_ingreso = max(productos_kpi, key=lambda x: x.ingreso_esperado) if productos_kpi else None
    
    return KPIsResponse(
        total_productos=len(productos_kpi),
        ingreso_total_esperado=round(ingreso_total, 2),
        ganancia_total_esperada=round(ganancia_total, 2),
        costo_total_esperado=round(costo_total, 2),
        producto_mayor_volumen=producto_mayor_volumen,
        producto_mayor_rentabilidad=producto_mayor_rentabilidad,
        producto_mayor_ingreso=producto_mayor_ingreso,
        productos=productos_kpi
    )


@router.get("/{prediccion_id}", response_model=PrediccionResponse)
async def get_prediccion(
    prediccion_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    repo = PrediccionRepository(db)
    prediccion = await repo.get_by_id(prediccion_id)
    if not prediccion:
        raise HTTPException(status_code=404, detail="Predicción no encontrada")
    return prediccion


@router.get("/producto/{producto_id}", response_model=List[PrediccionResponse])
async def get_predicciones_by_product(
    producto_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    repo = PrediccionRepository(db)
    return await repo.get_by_product(producto_id)


@router.get("/producto/{producto_id}/ultima", response_model=PrediccionResponse)
async def get_latest_prediccion(
    producto_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    repo = PrediccionRepository(db)
    prediccion = await repo.get_latest(producto_id)
    if not prediccion:
        raise HTTPException(status_code=404, detail="No hay predicciones para este producto")
    return prediccion


@router.post("", response_model=PrediccionResponse, status_code=201)
async def create_prediccion(
    data: PrediccionCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    repo = PrediccionRepository(db)
    prediccion = Prediccion(**data.model_dump())
    return await repo.create(prediccion)


@router.post("/predecir", response_model=List[PrediccionResponse], status_code=201)
async def predecir_demanda(
    data: PrediccionRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    """Genera predicciones de demanda usando ensemble (XGBoost + LightGBM) o modelo individual."""
    modelo_repo = ModeloIARepository(db)
    
    # Verificar si hay ensemble disponible
    use_ensemble = False
    modelo = None
    
    try:
        ensemble_data = ml_service.load_model("ensemble.pkl")
        use_ensemble = True
        modelo = await modelo_repo.get_active()
    except FileNotFoundError:
        pass
    
    if not use_ensemble:
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
    else:
        model = None

    result = await db.execute(
        text("""
            SELECT v.fecha_venta, dv.cantidad, dv.precio_unitario
            FROM detalle_venta dv
            JOIN venta v ON dv.id_venta = v.id_venta
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

    predicciones_raw = ml_service.predict_demand(
        model, features_df, data.horizonte_dias, use_ensemble=use_ensemble
    )

    repo = PrediccionRepository(db)
    hist_repo = HistorialPrediccionRepository(db)

    # Ajustar fechas si se proporciona fecha_inicio
    fecha_offset = None
    if data.fecha_inicio and predicciones_raw:
        primera_fecha = datetime.strptime(predicciones_raw[0]["fecha"], "%Y-%m-%d").date()
        fecha_offset = data.fecha_inicio - primera_fecha
    
    predicciones_obj = []
    for pred in predicciones_raw:
        fecha_pred = datetime.strptime(pred["fecha"], "%Y-%m-%d").date()
        
        if fecha_offset is not None:
            fecha_pred = fecha_pred + fecha_offset
        
        predicciones_obj.append(Prediccion(
            id_modelo=modelo.id_modelo if modelo else 0,
            id_producto=data.id_producto,
            fecha_prediccion=fecha_pred,
            periodo=fecha_pred.strftime("%Y-%m"),
            demanda_estimada=pred["demanda_estimada"],
            confianza_min=pred["confianza_min"],
            confianza_max=pred["confianza_max"],
            horizonte_dias=data.horizonte_dias,
            porcentaje_confianza=95.0,
        ))

    # Archivar predicciones anteriores en historial y eliminar de tabla activa
    await hist_repo.archivar_por_producto(data.id_producto, motivo="REEMPLAZADA")
    await repo.delete_by_product(data.id_producto)
    
    predicciones_creadas = await repo.create_many(predicciones_obj)
    return predicciones_creadas


@router.post("/predecir-lote", response_model=PrediccionBatchResponse)
async def predecir_lote(
    data: PrediccionBatchRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PREDICCION_IA_LEER"))
):
    """Genera predicciones para multiples productos con multiples modelos. Thread-safe con locks por producto."""
    modelo_repo = ModeloIARepository(db)
    repo = PrediccionRepository(db)
    hist_repo = HistorialPrediccionRepository(db)

    # Cargar todos los modelos solicitados
    modelos_cargados = {}
    for modelo_id in data.ids_modelos:
        modelo = await modelo_repo.get_by_id(modelo_id)
        if not modelo or not modelo.archivo_modelo:
            raise HTTPException(
                status_code=404,
                detail=f"Modelo {modelo_id} no encontrado o sin archivo"
            )
        try:
            # Cache: solo cargar si aun no esta en memoria
            if modelo_id not in modelos_cargados:
                modelos_cargados[modelo_id] = {
                    "modelo": modelo,
                    "ml_model": ml_service.load_model(modelo.archivo_modelo)
                }
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Archivo de modelo no encontrado: {modelo.archivo_modelo}"
            )

    exitosos = []
    fallidos = []
    errores = []

    async def predecir_producto_modelo(producto_id: int, modelo_id: int):
        """Predice un producto con un modelo especifico. Thread-safe con lock por producto."""
        # Lock por producto para evitar race conditions
        if producto_id not in _product_locks:
            _product_locks[producto_id] = asyncio.Lock()

        async with _product_locks[producto_id]:
            modelo_info = modelos_cargados[modelo_id]
            ml_model = modelo_info["ml_model"]

            # Obtener historial de ventas
            result = await db.execute(
                text("""
                    SELECT v.fecha_venta, dv.cantidad, dv.precio_unitario
                    FROM detalle_venta dv
                    JOIN venta v ON dv.id_venta = v.id_venta
                    WHERE dv.id_producto = :producto_id
                    ORDER BY v.fecha_venta ASC
                """),
                {"producto_id": producto_id}
            )
            rows = result.fetchall()

            if not rows:
                return False, f"Producto {producto_id}: Sin historial de ventas"

            historial_df = pd.DataFrame(rows, columns=["fecha_venta", "cantidad", "precio_unitario"])
            features_df = ml_service.prepare_features_from_history(historial_df)

            if len(features_df) < 30:
                return False, f"Producto {producto_id}: Historial insuficiente ({len(features_df)} dias)"

            # Ejecutar prediccion en thread pool (no bloquea event loop)
            loop = asyncio.get_event_loop()
            predicciones_raw = await loop.run_in_executor(
                _ml_executor,
                partial(ml_service.predict_demand, ml_model, features_df, data.horizonte_dias, use_ensemble=False)
            )

            # Ajustar fechas si se proporciona fecha_inicio
            fecha_offset = None
            if data.fecha_inicio and predicciones_raw:
                primera_fecha = datetime.strptime(predicciones_raw[0]["fecha"], "%Y-%m-%d").date()
                fecha_offset = data.fecha_inicio - primera_fecha

            predicciones_obj = []
            for pred in predicciones_raw:
                fecha_pred = datetime.strptime(pred["fecha"], "%Y-%m-%d").date()
                if fecha_offset is not None:
                    fecha_pred = fecha_pred + fecha_offset

                predicciones_obj.append(Prediccion(
                    id_modelo=modelo_id,
                    id_producto=producto_id,
                    fecha_prediccion=fecha_pred,
                    periodo=fecha_pred.strftime("%Y-%m"),
                    demanda_estimada=pred["demanda_estimada"],
                    confianza_min=pred["confianza_min"],
                    confianza_max=pred["confianza_max"],
                    horizonte_dias=data.horizonte_dias,
                    porcentaje_confianza=95.0,
                ))

            # Archivar y eliminar predicciones anteriores de ESTE producto + modelo
            await hist_repo.archivar_por_producto(producto_id, motivo="REEMPLAZADA", modelo_id=modelo_id)
            await repo.delete_by_product_and_model(producto_id, modelo_id)
            await repo.create_many(predicciones_obj)
            return True, None

    # Ejecutar todos los producto x modelo en paralelo
    tareas = []
    for producto_id in data.ids_productos:
        for modelo_id in data.ids_modelos:
            tareas.append(predecir_producto_modelo(producto_id, modelo_id))

    resultados = await asyncio.gather(*tareas, return_exceptions=True)

    for resultado in resultados:
        if isinstance(resultado, Exception):
            fallidos.append(0)
            errores.append(str(resultado))
        else:
            ok, error_msg = resultado
            if ok:
                exitosos.append(1)
            else:
                fallidos.append(0)
                errores.append(error_msg)

    return PrediccionBatchResponse(
        total_productos=len(data.ids_productos) * len(data.ids_modelos),
        exitosos=len(exitosos),
        fallidos=len(fallidos),
        productos_exitosos=exitosos,
        productos_fallidos=fallidos,
        detalle_errores=errores
    )
