from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.usuarios import Usuario
from typing import List, Optional


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Usuario]:
        result = await self.db.execute(select(Usuario))
        return list(result.scalars().all())

    async def get_by_email(self, email: str) -> Usuario | None:
        result = await self.db.execute(select(Usuario).where(Usuario.correo == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Usuario | None:
        result = await self.db.execute(select(Usuario).where(Usuario.id_usuario == user_id))
        return result.scalar_one_or_none()

    async def create(self, user: Usuario) -> Usuario:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: int, **kwargs) -> Optional[Usuario]:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True

    async def email_exists(self, email: str) -> bool:
        result = await self.db.execute(select(Usuario).where(Usuario.correo == email))
        return result.scalar_one_or_none() is not None
