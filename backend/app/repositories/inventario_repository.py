from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inventarios import Inventario
from typing import List, Optional


class InventarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Inventario]:
        result = await self.db.execute(select(Inventario))
        return list(result.scalars().all())

    async def get_by_id(self, inventario_id: int) -> Optional[Inventario]:
        result = await self.db.execute(select(Inventario).where(Inventario.id_inventario == inventario_id))
        return result.scalar_one_or_none()

    async def get_by_product(self, producto_id: int) -> Optional[Inventario]:
        result = await self.db.execute(select(Inventario).where(Inventario.id_producto == producto_id))
        return result.scalar_one_or_none()

    async def get_low_stock(self) -> List[Inventario]:
        result = await self.db.execute(
            select(Inventario).where(Inventario.stock_actual <= Inventario.stock_minimo)
        )
        return list(result.scalars().all())

    async def create(self, inventario: Inventario) -> Inventario:
        self.db.add(inventario)
        await self.db.commit()
        await self.db.refresh(inventario)
        return inventario

    async def update(self, inventario_id: int, **kwargs) -> Optional[Inventario]:
        inventario = await self.get_by_id(inventario_id)
        if not inventario:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(inventario, key, value)
        await self.db.commit()
        await self.db.refresh(inventario)
        return inventario

    async def update_stock(self, producto_id: int, cantidad: int, tipo: str) -> Optional[Inventario]:
        inventario = await self.get_by_product(producto_id)
        if not inventario:
            return None
        if tipo == "ENTRADA":
            inventario.stock_actual += cantidad
        elif tipo == "SALIDA":
            inventario.stock_actual -= cantidad
        await self.db.commit()
        await self.db.refresh(inventario)
        return inventario
