from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import (
    verify_password,
    hash_password,
    create_access_token,
    get_current_user,
    require_admin,
    set_token_cookie,
    clear_token_cookie,
)
from app.schemas.auth import UserCreate, UserLogin, UserResponse, UserUpdate, Token
from app.models.usuarios import Usuario
from typing import List

router = APIRouter(prefix="/api/auth", tags=["Auth"])

_login_attempts = {}
_MAX_ATTEMPTS = 5
_LOCKOUT_SECONDS = 300


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)

    if await repo.email_exists(data.correo):
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    from sqlalchemy import select
    from app.models.roles import Rol
    result = await db.execute(select(Rol).where(Rol.nombre == "VENTAS"))
    rol = result.scalar_one_or_none()
    if not rol:
        raise HTTPException(status_code=500, detail="Rol por defecto no encontrado")

    user = Usuario(
        id_rol=rol.id_rol,
        nombres=data.nombres,
        apellidos=data.apellidos,
        correo=data.correo,
        password_hash=hash_password(data.password),
    )
    created = await repo.create(user)
    return created


@router.post("/login", response_model=Token)
async def login(data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    import time
    now = time.time()
    email = data.correo.lower().strip()

    if email in _login_attempts:
        attempts, lockout_until = _login_attempts[email]
        if lockout_until and now < lockout_until:
            remaining = int(lockout_until - now)
            raise HTTPException(status_code=429, detail=f"Demasiados intentos. Intente de nuevo en {remaining} segundos")
        if lockout_until and now >= lockout_until:
            _login_attempts[email] = (0, None)

    repo = UserRepository(db)
    user = await repo.get_by_email(data.correo)

    if not user or not verify_password(data.password, user.password_hash):
        attempts, _ = _login_attempts.get(email, (0, None))
        attempts += 1
        lockout_until = now + _LOCKOUT_SECONDS if attempts >= _MAX_ATTEMPTS else None
        _login_attempts[email] = (attempts, lockout_until)
        if attempts >= _MAX_ATTEMPTS:
            raise HTTPException(status_code=429, detail="Demasiados intentos. Cuenta bloqueada temporalmente")
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    _login_attempts.pop(email, None)

    if not user.estado:
        raise HTTPException(status_code=403, detail="Usuario desactivado")

    token = create_access_token({"sub": str(user.id_usuario)})
    
    set_token_cookie(response, token)
    
    return Token(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
async def logout(response: Response):
    clear_token_cookie(response)
    return {"message": "Sesión cerrada correctamente"}


@router.get("/me", response_model=UserResponse)
async def get_me(user: Usuario = Depends(get_current_user)):
    return user


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin)
):
    repo = UserRepository(db)
    return await repo.get_all()


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin)
):
    repo = UserRepository(db)
    existing = await repo.get_by_id(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = hash_password(update_data.pop("password"))
    else:
        update_data.pop("password", None)

    updated = await repo.update(user_id, **update_data)
    return updated


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin)
):
    repo = UserRepository(db)
    if user_id == user.id_usuario:
        raise HTTPException(status_code=400, detail="No puede eliminarse a sí mismo")
    if not await repo.delete(user_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado"}
