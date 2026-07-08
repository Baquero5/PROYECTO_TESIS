from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.repositories.tienda_repository import TiendaRepository
from app.schemas.tienda import TiendaCreate, TiendaUpdate, TiendaResponse
from app.models.tiendas import Tienda
from app.services.auth_service import require_permission
from typing import List

router = APIRouter(prefix="/api/tiendas", tags=["Tiendas"])


@router.get("", response_model=List[TiendaResponse])
async def get_tiendas(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("CONFIGURACION_LEER"))
):
    repo = TiendaRepository(db)
    return await repo.get_all()


@router.get("/{tienda_id}", response_model=TiendaResponse)
async def get_tienda(
    tienda_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("CONFIGURACION_LEER"))
):
    repo = TiendaRepository(db)
    tienda = await repo.get_by_id(tienda_id)
    if not tienda:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return tienda


@router.post("", response_model=TiendaResponse, status_code=201)
async def create_tienda(
    data: TiendaCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("CONFIGURACION_CREAR"))
):
    repo = TiendaRepository(db)
    tienda = Tienda(**data.model_dump())
    try:
        return await repo.create(tienda)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una tienda con ese nombre")


@router.put("/{tienda_id}", response_model=TiendaResponse)
async def update_tienda(
    tienda_id: int,
    data: TiendaUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("CONFIGURACION_ACTUALIZAR"))
):
    repo = TiendaRepository(db)
    tienda = await repo.update(tienda_id, **data.model_dump(exclude_unset=True))
    if not tienda:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return tienda


@router.delete("/{tienda_id}")
async def delete_tienda(
    tienda_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("CONFIGURACION_ELIMINAR"))
):
    repo = TiendaRepository(db)
    if not await repo.delete(tienda_id):
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return {"message": "Tienda eliminada"}
