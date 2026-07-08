from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.predicciones import Prediccion
from typing import List, Optional
from datetime import date


class PrediccionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Prediccion]:
        result = await self.db.execute(select(Prediccion))
        return list(result.scalars().all())

    async def get_by_id(self, prediccion_id: int) -> Optional[Prediccion]:
        result = await self.db.execute(
            select(Prediccion).where(Prediccion.id_prediccion == prediccion_id)
        )
        return result.scalar_one_or_none()

    async def get_by_product(self, producto_id: int) -> List[Prediccion]:
        result = await self.db.execute(
            select(Prediccion).where(Prediccion.id_producto == producto_id)
        )
        return list(result.scalars().all())

    async def get_latest(self, producto_id: int) -> Optional[Prediccion]:
        result = await self.db.execute(
            select(Prediccion)
            .where(Prediccion.id_producto == producto_id)
            .order_by(Prediccion.fecha_prediccion.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_model(self, modelo_id: int) -> List[Prediccion]:
        result = await self.db.execute(
            select(Prediccion).where(Prediccion.id_modelo == modelo_id)
        )
        return list(result.scalars().all())

    async def get_with_pagination(self, skip: int = 0, limit: int = 100) -> List[Prediccion]:
        result = await self.db.execute(
            select(Prediccion).offset(skip).limit(limit).order_by(desc(Prediccion.fecha_prediccion))
        )
        return list(result.scalars().all())

    async def create(self, prediccion: Prediccion) -> Prediccion:
        self.db.add(prediccion)
        await self.db.commit()
        await self.db.refresh(prediccion)
        return prediccion

    async def create_many(self, predicciones: List[Prediccion]) -> List[Prediccion]:
        self.db.add_all(predicciones)
        await self.db.commit()
        for p in predicciones:
            await self.db.refresh(p)
        return predicciones

    async def delete_by_product(self, producto_id: int) -> int:
        from sqlalchemy import delete
        result = await self.db.execute(
            delete(Prediccion).where(Prediccion.id_producto == producto_id)
        )
        await self.db.commit()
        return result.rowcount

    async def delete_by_product_and_model(self, producto_id: int, modelo_id: int) -> int:
        from sqlalchemy import delete
        result = await self.db.execute(
            delete(Prediccion).where(
                Prediccion.id_producto == producto_id,
                Prediccion.id_modelo == modelo_id
            )
        )
        await self.db.commit()
        return result.rowcount
