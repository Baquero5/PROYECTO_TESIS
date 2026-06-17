from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import (
    verify_password,
    hash_password,
    create_access_token,
    get_current_user,
)
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token
from app.models.usuarios import Usuario

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)

    if await repo.email_exists(data.correo):
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    user = Usuario(
        id_rol=data.id_rol,
        nombres=data.nombres,
        apellidos=data.apellidos,
        correo=data.correo,
        password_hash=hash_password(data.password),
    )
    created = await repo.create(user)
    return created


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_by_email(data.correo)

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    if not user.estado:
        raise HTTPException(status_code=403, detail="Usuario desactivado")

    token = create_access_token({"sub": str(user.id_usuario)})
    return Token(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: Usuario = Depends(get_current_user)):
    return user
