from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.movimientos_inventario import MovimientoInventario
from typing import List, Optional


class MovimientoInventarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[MovimientoInventario]:
        result = await self.db.execute(select(MovimientoInventario))
        return list(result.scalars().all())

    async def get_by_id(self, movimiento_id: int) -> Optional[MovimientoInventario]:
        result = await self.db.execute(
            select(MovimientoInventario).where(MovimientoInventario.id_movimiento == movimiento_id)
        )
        return result.scalar_one_or_none()

    async def get_by_product(self, producto_id: int) -> List[MovimientoInventario]:
        result = await self.db.execute(
            select(MovimientoInventario).where(MovimientoInventario.id_producto == producto_id)
        )
        return list(result.scalars().all())

    async def create(self, movimiento: MovimientoInventario) -> MovimientoInventario:
        self.db.add(movimiento)
        await self.db.commit()
        await self.db.refresh(movimiento)
        return movimiento
