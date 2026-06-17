from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.reabastecimiento_repository import ReabastecimientoRepository
from app.schemas.reabastecimiento import ReabastecimientoCreate, ReabastecimientoUpdate, ReabastecimientoResponse
from typing import List

router = APIRouter(prefix="/api/reabastecimiento", tags=["Reabastecimiento"])


@router.get("", response_model=List[ReabastecimientoResponse])
async def get_reabastecimientos(db: AsyncSession = Depends(get_db)):
    repo = ReabastecimientoRepository(db)
    return await repo.get_all()


@router.get("/pendientes", response_model=List[ReabastecimientoResponse])
async def get_pending(db: AsyncSession = Depends(get_db)):
    repo = ReabastecimientoRepository(db)
    return await repo.get_pending()


@router.get("/{reabastecimiento_id}", response_model=ReabastecimientoResponse)
async def get_reabastecimiento(reabastecimiento_id: int, db: AsyncSession = Depends(get_db)):
    repo = ReabastecimientoRepository(db)
    reabastecimiento = await repo.get_by_id(reabastecimiento_id)
    if not reabastecimiento:
        raise HTTPException(status_code=404, detail="Reabastecimiento no encontrado")
    return reabastecimiento


@router.post("", response_model=ReabastecimientoResponse, status_code=201)
async def create_reabastecimiento(data: ReabastecimientoCreate, db: AsyncSession = Depends(get_db)):
    repo = ReabastecimientoRepository(db)
    from app.models.reabastecimiento import Reabastecimiento
    reabastecimiento = Reabastecimiento(**data.model_dump())
    return await repo.create(reabastecimiento)


@router.put("/{reabastecimiento_id}", response_model=ReabastecimientoResponse)
async def update_reabastecimiento(reabastecimiento_id: int, data: ReabastecimientoUpdate, db: AsyncSession = Depends(get_db)):
    repo = ReabastecimientoRepository(db)
    reabastecimiento = await repo.update(reabastecimiento_id, **data.model_dump(exclude_unset=True))
    if not reabastecimiento:
        raise HTTPException(status_code=404, detail="Reabastecimiento no encontrado")
    return reabastecimiento
