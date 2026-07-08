from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tiendas import Tienda
from typing import List, Optional


class TiendaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Tienda]:
        result = await self.db.execute(select(Tienda))
        return list(result.scalars().all())

    async def get_by_id(self, tienda_id: int) -> Optional[Tienda]:
        result = await self.db.execute(select(Tienda).where(Tienda.id_tienda == tienda_id))
        return result.scalar_one_or_none()

    async def create(self, tienda: Tienda) -> Tienda:
        self.db.add(tienda)
        await self.db.commit()
        await self.db.refresh(tienda)
        return tienda

    async def update(self, tienda_id: int, **kwargs) -> Optional[Tienda]:
        tienda = await self.get_by_id(tienda_id)
        if not tienda:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(tienda, key, value)
        await self.db.commit()
        await self.db.refresh(tienda)
        return tienda

    async def delete(self, tienda_id: int) -> bool:
        tienda = await self.get_by_id(tienda_id)
        if not tienda:
            return False
        await self.db.delete(tienda)
        await self.db.commit()
        return True
