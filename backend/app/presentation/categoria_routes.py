from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.repositories.categoria_repository import CategoriaRepository
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from app.models.categorias import Categoria
from typing import List

router = APIRouter(prefix="/api/categorias", tags=["Categorias"])


@router.get("", response_model=List[CategoriaResponse])
async def get_categorias(db: AsyncSession = Depends(get_db)):
    repo = CategoriaRepository(db)
    return await repo.get_all()


@router.get("/{categoria_id}", response_model=CategoriaResponse)
async def get_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    repo = CategoriaRepository(db)
    categoria = await repo.get_by_id(categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria


@router.post("", response_model=CategoriaResponse, status_code=201)
async def create_categoria(data: CategoriaCreate, db: AsyncSession = Depends(get_db)):
    repo = CategoriaRepository(db)
    categoria = Categoria(**data.model_dump())
    try:
        return await repo.create(categoria)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una categoria con ese nombre")


@router.put("/{categoria_id}", response_model=CategoriaResponse)
async def update_categoria(categoria_id: int, data: CategoriaUpdate, db: AsyncSession = Depends(get_db)):
    repo = CategoriaRepository(db)
    categoria = await repo.update(categoria_id, **data.model_dump(exclude_unset=True))
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria


@router.delete("/{categoria_id}")
async def delete_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    repo = CategoriaRepository(db)
    if not await repo.delete(categoria_id):
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"message": "Categoría eliminada"}
