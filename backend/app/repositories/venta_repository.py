from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ventas import Venta
from app.models.detalle_ventas import DetalleVenta
from typing import List, Optional


class VentaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Venta]:
        result = await self.db.execute(select(Venta).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, venta_id: int) -> Optional[Venta]:
        result = await self.db.execute(select(Venta).where(Venta.id_venta == venta_id))
        return result.scalar_one_or_none()

    async def get_by_user(self, usuario_id: int) -> List[Venta]:
        result = await self.db.execute(select(Venta).where(Venta.id_usuario == usuario_id))
        return list(result.scalars().all())

    async def create(self, venta: Venta) -> Venta:
        self.db.add(venta)
        await self.db.commit()
        await self.db.refresh(venta)
        return venta

    async def get_details(self, venta_id: int) -> List[DetalleVenta]:
        result = await self.db.execute(
            select(DetalleVenta).where(DetalleVenta.id_venta == venta_id)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.db.execute(select(func.count(Venta.id_venta)))
        return result.scalar()
