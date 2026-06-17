from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.detalle_ventas import DetalleVenta
from typing import List, Optional


class DetalleVentaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_sale(self, venta_id: int) -> List[DetalleVenta]:
        result = await self.db.execute(
            select(DetalleVenta).where(DetalleVenta.id_venta == venta_id)
        )
        return list(result.scalars().all())

    async def create(self, detalle: DetalleVenta) -> DetalleVenta:
        self.db.add(detalle)
        await self.db.commit()
        await self.db.refresh(detalle)
        return detalle

    async def create_many(self, detalles: List[DetalleVenta]) -> List[DetalleVenta]:
        for detalle in detalles:
            self.db.add(detalle)
        await self.db.commit()
        for detalle in detalles:
            await self.db.refresh(detalle)
        return detalles
