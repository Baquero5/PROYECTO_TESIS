from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alertas import Alerta
from typing import List, Optional


class AlertaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Alerta]:
        result = await self.db.execute(select(Alerta).order_by(Alerta.fecha_alerta.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, alerta_id: int) -> Optional[Alerta]:
        result = await self.db.execute(select(Alerta).where(Alerta.id_alerta == alerta_id))
        return result.scalar_one_or_none()

    async def get_active(self) -> List[Alerta]:
        result = await self.db.execute(
            select(Alerta).where(Alerta.estado == "ACTIVA").order_by(Alerta.fecha_alerta.desc())
        )
        return list(result.scalars().all())

    async def get_active_by_product(self, producto_id: int) -> Optional[Alerta]:
        result = await self.db.execute(
            select(Alerta).where(
                Alerta.id_producto == producto_id,
                Alerta.estado == "ACTIVA"
            )
        )
        return result.scalar_one_or_none()

    async def get_unread(self) -> List[Alerta]:
        result = await self.db.execute(
            select(Alerta).where(
                Alerta.leida == False,
                Alerta.estado == "ACTIVA"
            ).order_by(Alerta.fecha_alerta.desc())
        )
        return list(result.scalars().all())

    async def get_by_product(self, producto_id: int) -> List[Alerta]:
        result = await self.db.execute(
            select(Alerta).where(Alerta.id_producto == producto_id).order_by(Alerta.fecha_alerta.desc())
        )
        return list(result.scalars().all())

    async def create(self, alerta: Alerta) -> Alerta:
        self.db.add(alerta)
        await self.db.commit()
        await self.db.refresh(alerta)
        return alerta

    async def update(self, alerta_id: int, **kwargs) -> Optional[Alerta]:
        alerta = await self.get_by_id(alerta_id)
        if not alerta:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(alerta, key, value)
        await self.db.commit()
        await self.db.refresh(alerta)
        return alerta

    async def mark_as_read(self, alerta_id: int):
        alerta = await self.get_by_id(alerta_id)
        if alerta:
            alerta.leida = True
            await self.db.commit()

    async def mark_all_read(self):
        await self.db.execute(
            update(Alerta).where(Alerta.leida == False).values(leida=True)
        )
        await self.db.commit()

    async def delete(self, alerta_id: int) -> bool:
        alerta = await self.get_by_id(alerta_id)
        if not alerta:
            return False
        await self.db.delete(alerta)
        await self.db.commit()
        return True
