from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.alerta_repository import AlertaRepository
from app.repositories.inventario_repository import InventarioRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.alerta import AlertaCreate, AlertaUpdate, AlertaResponse
from app.models.alertas import Alerta
from app.services.auth_service import require_permission
from typing import List

router = APIRouter(prefix="/api/alertas", tags=["Alertas"])


def _alerta_to_response(alerta: Alerta) -> AlertaResponse:
    return AlertaResponse(
        id_alerta=alerta.id_alerta,
        id_producto=alerta.id_producto,
        tipo_alerta=alerta.tipo_alerta,
        mensaje=alerta.mensaje,
        fecha_alerta=alerta.fecha_alerta,
        estado=alerta.estado,
        leida=alerta.leida if alerta.leida is not None else False,
    )


@router.get("", response_model=List[AlertaResponse])
async def get_alertas(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("ALERTAS_LEER"))
):
    repo = AlertaRepository(db)
    alertas = await repo.get_all()
    return [_alerta_to_response(a) for a in alertas]


@router.get("/activas", response_model=List[AlertaResponse])
async def get_active_alertas(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("ALERTAS_LEER"))
):
    repo = AlertaRepository(db)
    alertas = await repo.get_active()
    return [_alerta_to_response(a) for a in alertas]


@router.get("/no-leidas", response_model=List[AlertaResponse])
async def get_unread_alertas(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("ALERTAS_LEER"))
):
    repo = AlertaRepository(db)
    alertas = await repo.get_unread()
    return [_alerta_to_response(a) for a in alertas]


@router.get("/contador")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("ALERTAS_LEER"))
):
    repo = AlertaRepository(db)
    alertas = await repo.get_unread()
    return {"count": len(alertas)}


@router.get("/producto/{producto_id}", response_model=List[AlertaResponse])
async def get_alertas_by_product(
    producto_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("ALERTAS_LEER"))
):
    repo = AlertaRepository(db)
    alertas = await repo.get_by_product(producto_id)
    return [_alerta_to_response(a) for a in alertas]


@router.get("/{alerta_id}", response_model=AlertaResponse)
async def get_alerta(
    alerta_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("ALERTAS_LEER"))
):
    repo = AlertaRepository(db)
    alerta = await repo.get_by_id(alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return _alerta_to_response(alerta)


@router.post("", response_model=AlertaResponse, status_code=201)
async def create_alerta(
    data: AlertaCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("ALERTAS_CREAR"))
):
    repo = AlertaRepository(db)
    alerta = Alerta(**data.model_dump())
    created = await repo.create(alerta)
    return _alerta_to_response(created)


@router.put("/{alerta_id}", response_model=AlertaResponse)
async def update_alerta(
    alerta_id: int,
    data: AlertaUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("ALERTAS_ACTUALIZAR"))
):
    repo = AlertaRepository(db)
    update_data = data.model_dump(exclude_unset=True)
    leida_value = update_data.pop("leida", None)
    alerta = await repo.update(alerta_id, **update_data)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    if leida_value is True:
        await repo.mark_as_read(alerta_id)
        alerta.leida = True
    return _alerta_to_response(alerta)


@router.put("/{alerta_id}/marcar-leida")
async def mark_as_read(
    alerta_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("ALERTAS_ACTUALIZAR"))
):
    repo = AlertaRepository(db)
    alerta = await repo.get_by_id(alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    await repo.mark_as_read(alerta_id)
    return {"message": "Alerta marcada como leída"}


@router.put("/marcar-todas-leidas")
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("ALERTAS_ACTUALIZAR"))
):
    repo = AlertaRepository(db)
    await repo.mark_all_read()
    return {"message": "Todas las alertas marcadas como leídas"}


@router.post("/detectar")
async def detect_alerts(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("ALERTAS_CREAR"))
):
    alertas_creadas = []
    inv_repo = InventarioRepository(db)
    al_repo = AlertaRepository(db)
    prod_repo = ProductRepository(db)

    inventarios = await inv_repo.get_all()

    for inv in inventarios:
        existe_critica = await al_repo.get_active_by_product(inv.id_producto, "CRITICA")
        existe_preventiva = await al_repo.get_active_by_product(inv.id_producto, "PREVENTIVA")

        producto = await prod_repo.get_by_id(inv.id_producto)
        nombre_producto = producto.nombre if producto else f"#{inv.id_producto}"

        if inv.stock_actual <= inv.stock_minimo and inv.stock_minimo > 0:
            if existe_critica:
                continue
            alerta = Alerta(
                id_producto=inv.id_producto,
                tipo_alerta="CRITICA",
                mensaje=f"Stock crítico de '{nombre_producto}': {inv.stock_actual} unidades (mínimo: {inv.stock_minimo})",
                estado="ACTIVA",
            )
            await al_repo.create(alerta)
            alertas_creadas.append({"producto": nombre_producto, "tipo": "CRITICA"})

        elif inv.stock_maximo > 0 and inv.stock_actual <= inv.stock_minimo * 1.5 and inv.stock_minimo > 0:
            if existe_preventiva:
                continue
            alerta = Alerta(
                id_producto=inv.id_producto,
                tipo_alerta="PREVENTIVA",
                mensaje=f"Stock bajo de '{nombre_producto}': {inv.stock_actual} unidades (mínimo: {inv.stock_minimo})",
                estado="ACTIVA",
            )
            await al_repo.create(alerta)
            alertas_creadas.append({"producto": nombre_producto, "tipo": "PREVENTIVA"})

    return {
        "message": f"Detección completada. {len(alertas_creadas)} nueva(s) alerta(s)",
        "alertas_creadas": alertas_creadas,
    }


@router.delete("/{alerta_id}")
async def delete_alerta(
    alerta_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("ALERTAS_ELIMINAR"))
):
    repo = AlertaRepository(db)
    alerta = await repo.get_by_id(alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    await repo.delete(alerta_id)
    return {"message": "Alerta eliminada"}
