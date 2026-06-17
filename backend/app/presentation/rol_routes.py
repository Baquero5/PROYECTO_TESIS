from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.rol_repository import RolRepository
from app.schemas.rol import RolCreate, RolUpdate, RolResponse
from app.models.roles import Rol
from typing import List

router = APIRouter(prefix="/api/roles", tags=["Roles"])


@router.get("", response_model=List[RolResponse])
async def get_roles(db: AsyncSession = Depends(get_db)):
    repo = RolRepository(db)
    return await repo.get_all()


@router.get("/{rol_id}", response_model=RolResponse)
async def get_rol(rol_id: int, db: AsyncSession = Depends(get_db)):
    repo = RolRepository(db)
    rol = await repo.get_by_id(rol_id)
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol


@router.post("", response_model=RolResponse, status_code=201)
async def create_rol(data: RolCreate, db: AsyncSession = Depends(get_db)):
    repo = RolRepository(db)
    if await repo.get_by_name(data.nombre):
        raise HTTPException(status_code=400, detail="El nombre del rol ya existe")
    rol = Rol(**data.model_dump())
    return await repo.create(rol)


@router.put("/{rol_id}", response_model=RolResponse)
async def update_rol(rol_id: int, data: RolUpdate, db: AsyncSession = Depends(get_db)):
    repo = RolRepository(db)
    rol = await repo.update(rol_id, **data.model_dump(exclude_unset=True))
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol


@router.delete("/{rol_id}")
async def delete_rol(rol_id: int, db: AsyncSession = Depends(get_db)):
    repo = RolRepository(db)
    if not await repo.delete(rol_id):
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return {"message": "Rol eliminado"}
