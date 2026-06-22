from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.permiso_repository import PermisoRepository
from app.schemas.permiso import PermisoCreate, PermisoUpdate, PermisoResponse, RolPermisoCreate
from app.models.permisos import Permiso
from app.services.auth_service import require_admin
from typing import List

router = APIRouter(prefix="/api/permisos", tags=["Permisos"])


@router.get("", response_model=List[PermisoResponse])
async def get_permisos(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin)
):
    repo = PermisoRepository(db)
    return await repo.get_all()


@router.get("/{permiso_id}", response_model=PermisoResponse)
async def get_permiso(
    permiso_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin)
):
    repo = PermisoRepository(db)
    permiso = await repo.get_by_id(permiso_id)
    if not permiso:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    return permiso


@router.post("", response_model=PermisoResponse, status_code=201)
async def create_permiso(
    data: PermisoCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin)
):
    repo = PermisoRepository(db)
    if await repo.get_by_codigo(data.codigo):
        raise HTTPException(status_code=400, detail="El código del permiso ya existe")
    permiso = Permiso(**data.model_dump())
    return await repo.create(permiso)


@router.put("/{permiso_id}", response_model=PermisoResponse)
async def update_permiso(
    permiso_id: int,
    data: PermisoUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin)
):
    repo = PermisoRepository(db)
    permiso = await repo.update(permiso_id, **data.model_dump(exclude_unset=True))
    if not permiso:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    return permiso


@router.delete("/{permiso_id}")
async def delete_permiso(
    permiso_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin)
):
    repo = PermisoRepository(db)
    if not await repo.delete(permiso_id):
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    return {"message": "Permiso eliminado"}


@router.get("/rol/{rol_id}", response_model=List[PermisoResponse])
async def get_permisos_by_rol(
    rol_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin)
):
    repo = PermisoRepository(db)
    return await repo.get_permisos_by_rol(rol_id)


@router.post("/rol/{rol_id}")
async def assign_permisos_to_rol(
    rol_id: int,
    data: RolPermisoCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin)
):
    repo = PermisoRepository(db)
    await repo.assign_permisos_to_rol(rol_id, data.id_permisos)
    return {"message": "Permisos asignados correctamente"}


@router.delete("/rol/{rol_id}/permiso/{permiso_id}")
async def remove_permiso_from_rol(
    rol_id: int,
    permiso_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin)
):
    repo = PermisoRepository(db)
    if not await repo.remove_permiso_from_rol(rol_id, permiso_id):
        raise HTTPException(status_code=404, detail="Permiso no encontrado en el rol")
    return {"message": "Permiso removido del rol"}
