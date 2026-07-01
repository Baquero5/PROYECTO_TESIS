from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.proveedor_repository import ProveedorRepository
from app.schemas.proveedor import ProveedorCreate, ProveedorUpdate, ProveedorResponse
from app.models.proveedores import Proveedor
from app.services.auth_service import require_permission
from typing import List

router = APIRouter(prefix="/api/proveedores", tags=["Proveedores"])


@router.get("", response_model=List[ProveedorResponse])
async def get_proveedores(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PROVEEDORES_LEER"))
):
    repo = ProveedorRepository(db)
    return await repo.get_all()


@router.get("/{proveedor_id}", response_model=ProveedorResponse)
async def get_proveedor(
    proveedor_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PROVEEDORES_LEER"))
):
    repo = ProveedorRepository(db)
    proveedor = await repo.get_by_id(proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return proveedor


@router.post("", response_model=ProveedorResponse, status_code=201)
async def create_proveedor(
    data: ProveedorCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PROVEEDORES_CREAR"))
):
    repo = ProveedorRepository(db)
    if await repo.get_by_ruc(data.ruc):
        raise HTTPException(status_code=400, detail="El RUC ya está registrado")
    proveedor = Proveedor(**data.model_dump())
    return await repo.create(proveedor)


@router.put("/{proveedor_id}", response_model=ProveedorResponse)
async def update_proveedor(
    proveedor_id: int,
    data: ProveedorUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PROVEEDORES_ACTUALIZAR"))
):
    repo = ProveedorRepository(db)
    proveedor = await repo.update(proveedor_id, **data.model_dump(exclude_unset=True))
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return proveedor


@router.delete("/{proveedor_id}")
async def delete_proveedor(
    proveedor_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PROVEEDORES_ELIMINAR"))
):
    repo = ProveedorRepository(db)
    if not await repo.delete(proveedor_id):
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return {"message": "Proveedor eliminado"}
