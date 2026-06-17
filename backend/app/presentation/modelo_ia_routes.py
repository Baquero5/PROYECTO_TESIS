from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.modelo_ia_repository import ModeloIARepository
from app.schemas.modelo_ia import ModeloIACreate, ModeloIAUpdate, ModeloIAResponse
from typing import List

router = APIRouter(prefix="/api/modelos-ia", tags=["Modelos IA"])


@router.get("", response_model=List[ModeloIAResponse])
async def get_modelos(db: AsyncSession = Depends(get_db)):
    repo = ModeloIARepository(db)
    return await repo.get_all()


@router.get("/mejor", response_model=ModeloIAResponse)
async def get_best_modelo(db: AsyncSession = Depends(get_db)):
    repo = ModeloIARepository(db)
    modelo = await repo.get_best()
    if not modelo:
        raise HTTPException(status_code=404, detail="No hay modelos entrenados")
    return modelo


@router.get("/{modelo_id}", response_model=ModeloIAResponse)
async def get_modelo(modelo_id: int, db: AsyncSession = Depends(get_db)):
    repo = ModeloIARepository(db)
    modelo = await repo.get_by_id(modelo_id)
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    return modelo


@router.post("", response_model=ModeloIAResponse, status_code=201)
async def create_modelo(data: ModeloIACreate, db: AsyncSession = Depends(get_db)):
    repo = ModeloIARepository(db)
    from app.models.modelos_ia import ModeloIA
    modelo = ModeloIA(**data.model_dump())
    return await repo.create(modelo)


@router.put("/{modelo_id}", response_model=ModeloIAResponse)
async def update_modelo(modelo_id: int, data: ModeloIAUpdate, db: AsyncSession = Depends(get_db)):
    repo = ModeloIARepository(db)
    modelo = await repo.update(modelo_id, **data.model_dump(exclude_unset=True))
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    return modelo
