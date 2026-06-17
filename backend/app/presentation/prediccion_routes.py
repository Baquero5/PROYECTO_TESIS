from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.prediccion_repository import PrediccionRepository
from app.schemas.prediccion import PrediccionCreate, PrediccionResponse
from typing import List

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
    from app.models.predicciones import Prediccion
    prediccion = Prediccion(**data.model_dump())
    return await repo.create(prediccion)
