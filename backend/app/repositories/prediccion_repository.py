from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.predicciones import Prediccion
from typing import List, Optional


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

    async def create(self, prediccion: Prediccion) -> Prediccion:
        self.db.add(prediccion)
        await self.db.commit()
        await self.db.refresh(prediccion)
        return prediccion
