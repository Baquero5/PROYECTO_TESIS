from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.usuarios import Usuario


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

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

    async def email_exists(self, email: str) -> bool:
        result = await self.db.execute(select(Usuario).where(Usuario.correo == email))
        return result.scalar_one_or_none() is not None
