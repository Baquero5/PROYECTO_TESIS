from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.dataset_repository import DatasetRepository
from app.schemas.dataset import DatasetCreate, DatasetUpdate, DatasetResponse
from typing import List

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])


@router.get("", response_model=List[DatasetResponse])
async def get_datasets(db: AsyncSession = Depends(get_db)):
    repo = DatasetRepository(db)
    return await repo.get_all()


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: int, db: AsyncSession = Depends(get_db)):
    repo = DatasetRepository(db)
    dataset = await repo.get_by_id(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")
    return dataset


@router.post("", response_model=DatasetResponse, status_code=201)
async def create_dataset(data: DatasetCreate, db: AsyncSession = Depends(get_db)):
    repo = DatasetRepository(db)
    from app.models.dataset_entrenamiento import DatasetEntrenamiento
    dataset = DatasetEntrenamiento(**data.model_dump())
    return await repo.create(dataset)


@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(dataset_id: int, data: DatasetUpdate, db: AsyncSession = Depends(get_db)):
    repo = DatasetRepository(db)
    dataset = await repo.update(dataset_id, **data.model_dump(exclude_unset=True))
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")
    return dataset
