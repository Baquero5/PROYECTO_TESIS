from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.roles import Rol
from typing import List, Optional


class RolRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Rol]:
        result = await self.db.execute(select(Rol))
        return list(result.scalars().all())

    async def get_by_id(self, rol_id: int) -> Optional[Rol]:
        result = await self.db.execute(select(Rol).where(Rol.id_rol == rol_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, nombre: str) -> Optional[Rol]:
        result = await self.db.execute(select(Rol).where(Rol.nombre == nombre))
        return result.scalar_one_or_none()

    async def create(self, rol: Rol) -> Rol:
        self.db.add(rol)
        await self.db.commit()
        await self.db.refresh(rol)
        return rol

    async def update(self, rol_id: int, **kwargs) -> Optional[Rol]:
        rol = await self.get_by_id(rol_id)
        if not rol:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(rol, key, value)
        await self.db.commit()
        await self.db.refresh(rol)
        return rol

    async def delete(self, rol_id: int) -> bool:
        rol = await self.get_by_id(rol_id)
        if not rol:
            return False
        await self.db.delete(rol)
        await self.db.commit()
        return True
