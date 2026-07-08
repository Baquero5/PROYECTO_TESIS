from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.repositories.subcategoria_repository import SubcategoriaRepository
from app.schemas.subcategoria import SubcategoriaCreate, SubcategoriaUpdate, SubcategoriaResponse
from app.models.subcategorias import Subcategoria
from app.services.auth_service import require_permission
from typing import List

router = APIRouter(prefix="/api/subcategorias", tags=["Subcategorias"])


@router.get("", response_model=List[SubcategoriaResponse])
async def get_subcategorias(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("CATEGORIAS_LEER"))
):
    repo = SubcategoriaRepository(db)
    return await repo.get_all()


@router.get("/categoria/{categoria_id}", response_model=List[SubcategoriaResponse])
async def get_subcategorias_by_categoria(
    categoria_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("CATEGORIAS_LEER"))
):
    repo = SubcategoriaRepository(db)
    return await repo.get_by_categoria(categoria_id)


@router.get("/{subcategoria_id}", response_model=SubcategoriaResponse)
async def get_subcategoria(
    subcategoria_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("CATEGORIAS_LEER"))
):
    repo = SubcategoriaRepository(db)
    sub = await repo.get_by_id(subcategoria_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subcategoría no encontrada")
    return sub


@router.post("", response_model=SubcategoriaResponse, status_code=201)
async def create_subcategoria(
    data: SubcategoriaCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("CATEGORIAS_CREAR"))
):
    repo = SubcategoriaRepository(db)
    subcategoria = Subcategoria(**data.model_dump())
    try:
        return await repo.create(subcategoria)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una subcategoría con ese nombre en esta categoría")


@router.put("/{subcategoria_id}", response_model=SubcategoriaResponse)
async def update_subcategoria(
    subcategoria_id: int,
    data: SubcategoriaUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("CATEGORIAS_ACTUALIZAR"))
):
    repo = SubcategoriaRepository(db)
    sub = await repo.update(subcategoria_id, **data.model_dump(exclude_unset=True))
    if not sub:
        raise HTTPException(status_code=404, detail="Subcategoría no encontrada")
    return sub


@router.delete("/{subcategoria_id}")
async def delete_subcategoria(
    subcategoria_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("CATEGORIAS_ELIMINAR"))
):
    repo = SubcategoriaRepository(db)
    if not await repo.delete(subcategoria_id):
        raise HTTPException(status_code=404, detail="Subcategoría no encontrada")
    return {"message": "Subcategoría eliminada"}
