from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ventas import Venta
from app.models.detalle_ventas import DetalleVenta
from typing import List, Optional
from datetime import datetime, timedelta


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

    async def get_sales_history_by_product(self, producto_id: int, days: int = 90) -> List[dict]:
        fecha_limite = datetime.now() - timedelta(days=days)
        
        result = await self.db.execute(
            select(
                Venta.fecha_venta,
                func.sum(DetalleVenta.cantidad).label("cantidad"),
                func.avg(DetalleVenta.precio_unitario).label("precio_unitario")
            )
            .join(DetalleVenta, Venta.id_venta == DetalleVenta.id_venta)
            .where(
                DetalleVenta.id_producto == producto_id,
                Venta.fecha_venta >= fecha_limite
            )
            .group_by(Venta.fecha_venta)
            .order_by(Venta.fecha_venta.asc())
        )
        rows = result.fetchall()
        return [{"fecha": str(row[0]), "cantidad": row[1], "precio": float(row[2])} for row in rows]
