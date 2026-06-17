from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.productos import Producto
from typing import List, Optional


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Producto]:
        result = await self.db.execute(
            select(Producto).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, product_id: int) -> Optional[Producto]:
        result = await self.db.execute(
            select(Producto).where(Producto.id_producto == product_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Producto]:
        result = await self.db.execute(
            select(Producto).where(Producto.codigo == code)
        )
        return result.scalar_one_or_none()

    async def create(self, product: Producto) -> Producto:
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update(self, product_id: int, **kwargs) -> Optional[Producto]:
        product = await self.get_by_id(product_id)
        if not product:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(product, key, value)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete(self, product_id: int) -> bool:
        product = await self.get_by_id(product_id)
        if not product:
            return False
        await self.db.delete(product)
        await self.db.commit()
        return True

    async def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        query = select(Producto).where(Producto.codigo == code)
        if exclude_id:
            query = query.where(Producto.id_producto != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def count(self) -> int:
        result = await self.db.execute(select(func.count(Producto.id_producto)))
        return result.scalar()
