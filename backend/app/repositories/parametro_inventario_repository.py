from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.parametros_inventario import ParametroInventario
from typing import List, Optional


class ParametroInventarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[ParametroInventario]:
        result = await self.db.execute(select(ParametroInventario))
        return list(result.scalars().all())

    async def get_by_id(self, parametro_id: int) -> Optional[ParametroInventario]:
        result = await self.db.execute(
            select(ParametroInventario).where(ParametroInventario.id_parametro == parametro_id)
        )
        return result.scalar_one_or_none()

    async def get_by_product(self, producto_id: int) -> Optional[ParametroInventario]:
        result = await self.db.execute(
            select(ParametroInventario).where(ParametroInventario.id_producto == producto_id)
        )
        return result.scalar_one_or_none()

    async def create(self, parametro: ParametroInventario) -> ParametroInventario:
        self.db.add(parametro)
        await self.db.commit()
        await self.db.refresh(parametro)
        return parametro

    async def update(self, parametro_id: int, **kwargs) -> Optional[ParametroInventario]:
        parametro = await self.get_by_id(parametro_id)
        if not parametro:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(parametro, key, value)
        await self.db.commit()
        await self.db.refresh(parametro)
        return parametro
