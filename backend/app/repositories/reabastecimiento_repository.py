from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.reabastecimiento import Reabastecimiento
from typing import List, Optional


class ReabastecimientoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Reabastecimiento]:
        result = await self.db.execute(select(Reabastecimiento))
        return list(result.scalars().all())

    async def get_by_id(self, reabastecimiento_id: int) -> Optional[Reabastecimiento]:
        result = await self.db.execute(
            select(Reabastecimiento).where(Reabastecimiento.id_reabastecimiento == reabastecimiento_id)
        )
        return result.scalar_one_or_none()

    async def get_pending(self) -> List[Reabastecimiento]:
        result = await self.db.execute(
            select(Reabastecimiento).where(Reabastecimiento.estado == "PENDIENTE")
        )
        return list(result.scalars().all())

    async def create(self, reabastecimiento: Reabastecimiento) -> Reabastecimiento:
        self.db.add(reabastecimiento)
        await self.db.commit()
        await self.db.refresh(reabastecimiento)
        return reabastecimiento

    async def update(self, reabastecimiento_id: int, **kwargs) -> Optional[Reabastecimiento]:
        reabastecimiento = await self.get_by_id(reabastecimiento_id)
        if not reabastecimiento:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(reabastecimiento, key, value)
        await self.db.commit()
        await self.db.refresh(reabastecimiento)
        return reabastecimiento
