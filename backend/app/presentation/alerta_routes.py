from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.alerta_repository import AlertaRepository
from app.schemas.alerta import AlertaCreate, AlertaUpdate, AlertaResponse
from typing import List

router = APIRouter(prefix="/api/alertas", tags=["Alertas"])


@router.get("", response_model=List[AlertaResponse])
async def get_alertas(db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    return await repo.get_all()


@router.get("/activas", response_model=List[AlertaResponse])
async def get_active_alertas(db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    return await repo.get_active()


@router.get("/{alerta_id}", response_model=AlertaResponse)
async def get_alerta(alerta_id: int, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    alerta = await repo.get_by_id(alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return alerta


@router.get("/producto/{producto_id}", response_model=List[AlertaResponse])
async def get_alertas_by_product(producto_id: int, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    return await repo.get_by_product(producto_id)


@router.post("", response_model=AlertaResponse, status_code=201)
async def create_alerta(data: AlertaCreate, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    from app.models.alertas import Alerta
    alerta = Alerta(**data.model_dump())
    return await repo.create(alerta)


@router.put("/{alerta_id}", response_model=AlertaResponse)
async def update_alerta(alerta_id: int, data: AlertaUpdate, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    alerta = await repo.update(alerta_id, **data.model_dump(exclude_unset=True))
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return alerta


@router.delete("/{alerta_id}")
async def delete_alerta(alerta_id: int, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    alerta = await repo.get_by_id(alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    await repo.delete(alerta_id)
    return {"message": "Alerta eliminada"}
