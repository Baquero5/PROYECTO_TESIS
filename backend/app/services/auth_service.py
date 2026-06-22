from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.models.usuarios import Usuario

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token inválido")

    repo = UserRepository(db)
    user = await repo.get_by_id(int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    if not user.estado:
        raise HTTPException(status_code=403, detail="Usuario desactivado")
    return user


async def require_admin(user: Usuario = Depends(get_current_user)) -> Usuario:
    from sqlalchemy import select
    from app.models.roles import Rol
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Rol).where(Rol.id_rol == user.id_rol))
        rol = result.scalar_one_or_none()
        if not rol or rol.nombre != "ADMINISTRADOR":
            raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
    return user


def require_permission(permission_code: str):
    async def permission_checker(
        user: Usuario = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> Usuario:
        from sqlalchemy import select
        from app.models.permisos import Permiso
        from app.models.rol_permisos import RolPermiso
        
        # Verificar si el usuario tiene el permiso
        result = await db.execute(
            select(Permiso)
            .join(RolPermiso, Permiso.id_permiso == RolPermiso.id_permiso)
            .where(
                RolPermiso.id_rol == user.id_rol,
                Permiso.codigo == permission_code
            )
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=403,
                detail=f"No tiene permiso para realizar esta acción: {permission_code}"
            )
        return user
    
    return Depends(permission_checker)
