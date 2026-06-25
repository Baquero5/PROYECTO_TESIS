from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.modelos_ia import ModeloIA
from typing import List, Optional


class ModeloIARepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[ModeloIA]:
        result = await self.db.execute(select(ModeloIA))
        return list(result.scalars().all())

    async def get_by_id(self, modelo_id: int) -> Optional[ModeloIA]:
        result = await self.db.execute(select(ModeloIA).where(ModeloIA.id_modelo == modelo_id))
        return result.scalar_one_or_none()

    async def get_best(self) -> Optional[ModeloIA]:
        result = await self.db.execute(
            select(ModeloIA)
            .where(ModeloIA.mape.isnot(None))
            .order_by(ModeloIA.mape.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_active(self) -> Optional[ModeloIA]:
        result = await self.db.execute(
            select(ModeloIA).where(ModeloIA.estado == "ACTIVO").limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_algorithm(self, algoritmo: str) -> List[ModeloIA]:
        result = await self.db.execute(
            select(ModeloIA).where(ModeloIA.algoritmo == algoritmo.upper())
        )
        return list(result.scalars().all())

    async def create(self, modelo: ModeloIA) -> ModeloIA:
        self.db.add(modelo)
        await self.db.commit()
        await self.db.refresh(modelo)
        return modelo

    async def update(self, modelo_id: int, **kwargs) -> Optional[ModeloIA]:
        modelo = await self.get_by_id(modelo_id)
        if not modelo:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(modelo, key, value)
        await self.db.commit()
        await self.db.refresh(modelo)
        return modelo

    async def activate_model(self, modelo_id: int) -> Optional[ModeloIA]:
        """Activa un modelo y desactiva los demás."""
        from sqlalchemy import update
        await self.db.execute(
            update(ModeloIA).values(estado="INACTIVO")
        )
        modelo = await self.get_by_id(modelo_id)
        if modelo:
            modelo.estado = "ACTIVO"
            await self.db.commit()
            await self.db.refresh(modelo)
        return modelo

    async def set_model_status(self, modelo_id: int, estado: str) -> Optional[ModeloIA]:
        """Establece el estado de un modelo sin afectar a otros."""
        modelo = await self.get_by_id(modelo_id)
        if modelo:
            modelo.estado = estado
            await self.db.commit()
            await self.db.refresh(modelo)
        return modelo
