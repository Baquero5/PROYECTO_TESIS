from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.parametro_inventario_repository import ParametroInventarioRepository
from app.schemas.parametro_inventario import ParametroInventarioCreate, ParametroInventarioUpdate, ParametroInventarioResponse
from app.models.parametros_inventario import ParametroInventario
from typing import List

router = APIRouter(prefix="/api/parametros-inventario", tags=["Parametros Inventario"])


@router.get("", response_model=List[ParametroInventarioResponse])
async def get_parametros(db: AsyncSession = Depends(get_db)):
    repo = ParametroInventarioRepository(db)
    return await repo.get_all()


@router.get("/{parametro_id}", response_model=ParametroInventarioResponse)
async def get_parametro(parametro_id: int, db: AsyncSession = Depends(get_db)):
    repo = ParametroInventarioRepository(db)
    parametro = await repo.get_by_id(parametro_id)
    if not parametro:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return parametro


@router.get("/producto/{producto_id}", response_model=ParametroInventarioResponse)
async def get_parametro_by_product(producto_id: int, db: AsyncSession = Depends(get_db)):
    repo = ParametroInventarioRepository(db)
    parametro = await repo.get_by_product(producto_id)
    if not parametro:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado para este producto")
    return parametro


@router.post("", response_model=ParametroInventarioResponse, status_code=201)
async def create_parametro(data: ParametroInventarioCreate, db: AsyncSession = Depends(get_db)):
    repo = ParametroInventarioRepository(db)
    if await repo.get_by_product(data.id_producto):
        raise HTTPException(status_code=400, detail="Ya existen parámetros para este producto")
    parametro = ParametroInventario(**data.model_dump())
    return await repo.create(parametro)


@router.put("/{parametro_id}", response_model=ParametroInventarioResponse)
async def update_parametro(parametro_id: int, data: ParametroInventarioUpdate, db: AsyncSession = Depends(get_db)):
    repo = ParametroInventarioRepository(db)
    parametro = await repo.update(parametro_id, **data.model_dump(exclude_unset=True))
    if not parametro:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return parametro
