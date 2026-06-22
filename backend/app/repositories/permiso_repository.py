from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.permisos import Permiso
from app.models.rol_permisos import RolPermiso
from typing import List, Optional


class PermisoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Permiso]:
        result = await self.db.execute(select(Permiso))
        return list(result.scalars().all())

    async def get_by_id(self, permiso_id: int) -> Optional[Permiso]:
        result = await self.db.execute(select(Permiso).where(Permiso.id_permiso == permiso_id))
        return result.scalar_one_or_none()

    async def get_by_codigo(self, codigo: str) -> Optional[Permiso]:
        result = await self.db.execute(select(Permiso).where(Permiso.codigo == codigo))
        return result.scalar_one_or_none()

    async def create(self, permiso: Permiso) -> Permiso:
        self.db.add(permiso)
        await self.db.commit()
        await self.db.refresh(permiso)
        return permiso

    async def update(self, permiso_id: int, **kwargs) -> Optional[Permiso]:
        permiso = await self.get_by_id(permiso_id)
        if not permiso:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(permiso, key, value)
        await self.db.commit()
        await self.db.refresh(permiso)
        return permiso

    async def delete(self, permiso_id: int) -> bool:
        permiso = await self.get_by_id(permiso_id)
        if not permiso:
            return False
        await self.db.delete(permiso)
        await self.db.commit()
        return True

    async def get_permisos_by_rol(self, rol_id: int) -> List[Permiso]:
        result = await self.db.execute(
            select(Permiso)
            .join(RolPermiso, Permiso.id_permiso == RolPermiso.id_permiso)
            .where(RolPermiso.id_rol == rol_id)
        )
        return list(result.scalars().all())

    async def assign_permisos_to_rol(self, rol_id: int, permiso_ids: List[int]) -> bool:
        # Eliminar permisos actuales del rol
        await self.db.execute(
            delete(RolPermiso).where(RolPermiso.id_rol == rol_id)
        )
        # Agregar nuevos permisos
        for permiso_id in permiso_ids:
            rol_permiso = RolPermiso(id_rol=rol_id, id_permiso=permiso_id)
            self.db.add(rol_permiso)
        await self.db.commit()
        return True

    async def remove_permiso_from_rol(self, rol_id: int, permiso_id: int) -> bool:
        result = await self.db.execute(
            delete(RolPermiso).where(
                RolPermiso.id_rol == rol_id,
                RolPermiso.id_permiso == permiso_id
            )
        )
        await self.db.commit()
        return result.rowcount > 0
