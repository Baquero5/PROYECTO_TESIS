from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.proveedores import Proveedor
from typing import List, Optional


class ProveedorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Proveedor]:
        result = await self.db.execute(select(Proveedor))
        return list(result.scalars().all())

    async def get_by_id(self, proveedor_id: int) -> Optional[Proveedor]:
        result = await self.db.execute(select(Proveedor).where(Proveedor.id_proveedor == proveedor_id))
        return result.scalar_one_or_none()

    async def get_by_ruc(self, ruc: str) -> Optional[Proveedor]:
        result = await self.db.execute(select(Proveedor).where(Proveedor.ruc == ruc))
        return result.scalar_one_or_none()

    async def create(self, proveedor: Proveedor) -> Proveedor:
        self.db.add(proveedor)
        await self.db.commit()
        await self.db.refresh(proveedor)
        return proveedor

    async def update(self, proveedor_id: int, **kwargs) -> Optional[Proveedor]:
        proveedor = await self.get_by_id(proveedor_id)
        if not proveedor:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(proveedor, key, value)
        await self.db.commit()
        await self.db.refresh(proveedor)
        return proveedor

    async def delete(self, proveedor_id: int) -> bool:
        proveedor = await self.get_by_id(proveedor_id)
        if not proveedor:
            return False
        await self.db.delete(proveedor)
        await self.db.commit()
        return True
