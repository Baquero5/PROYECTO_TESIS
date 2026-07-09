from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.subcategorias import Subcategoria
from typing import List, Optional


class SubcategoriaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Subcategoria]:
        result = await self.db.execute(select(Subcategoria))
        return list(result.scalars().all())

    async def get_by_id(self, subcategoria_id: int) -> Optional[Subcategoria]:
        result = await self.db.execute(select(Subcategoria).where(Subcategoria.id_subcategoria == subcategoria_id))
        return result.scalar_one_or_none()

    async def get_by_categoria(self, id_categoria: int) -> List[Subcategoria]:
        result = await self.db.execute(select(Subcategoria).where(Subcategoria.id_categoria == id_categoria))
        return list(result.scalars().all())

    async def create(self, subcategoria: Subcategoria) -> Subcategoria:
        self.db.add(subcategoria)
        await self.db.commit()
        await self.db.refresh(subcategoria)
        return subcategoria

    async def update(self, subcategoria_id: int, **kwargs) -> Optional[Subcategoria]:
        subcategoria = await self.get_by_id(subcategoria_id)
        if not subcategoria:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(subcategoria, key, value)
        await self.db.commit()
        await self.db.refresh(subcategoria)
        return subcategoria

    async def delete(self, subcategoria_id: int) -> bool:
        subcategoria = await self.get_by_id(subcategoria_id)
        if not subcategoria:
            return False
        await self.db.delete(subcategoria)
        await self.db.commit()
        return True
