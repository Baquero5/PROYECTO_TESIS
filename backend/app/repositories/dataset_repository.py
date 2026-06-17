from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dataset_entrenamiento import DatasetEntrenamiento
from typing import List, Optional


class DatasetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[DatasetEntrenamiento]:
        result = await self.db.execute(select(DatasetEntrenamiento))
        return list(result.scalars().all())

    async def get_by_id(self, dataset_id: int) -> Optional[DatasetEntrenamiento]:
        result = await self.db.execute(
            select(DatasetEntrenamiento).where(DatasetEntrenamiento.id_dataset == dataset_id)
        )
        return result.scalar_one_or_none()

    async def create(self, dataset: DatasetEntrenamiento) -> DatasetEntrenamiento:
        self.db.add(dataset)
        await self.db.commit()
        await self.db.refresh(dataset)
        return dataset

    async def update(self, dataset_id: int, **kwargs) -> Optional[DatasetEntrenamiento]:
        dataset = await self.get_by_id(dataset_id)
        if not dataset:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(dataset, key, value)
        await self.db.commit()
        await self.db.refresh(dataset)
        return dataset
