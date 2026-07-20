from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.models.productos import Producto
from app.services.auth_service import require_permission
from typing import List

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PRODUCTOS_LEER"))
):
    repo = ProductRepository(db)
    products = await repo.get_all(skip, limit)
    return products


@router.get("/stats/summary")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PRODUCTOS_LEER"))
):
    from sqlalchemy import text
    result = await db.execute(text("SELECT COUNT(*) as total FROM producto"))
    row = result.fetchone()
    total = row.total if row else 0

    result2 = await db.execute(text("SELECT COALESCE(SUM(precio_venta), 0) as total_value FROM producto"))
    row2 = result2.fetchone()
    total_value = float(row2.total_value) if row2 else 0.0

    return {
        "total_products": total,
        "total_inventory_value": round(total_value, 2)
    }


@router.get("/categoria/{categoria_id}", response_model=List[ProductResponse])
async def get_products_by_category(
    categoria_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PRODUCTOS_LEER"))
):
    repo = ProductRepository(db)
    return await repo.get_by_category(categoria_id)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PRODUCTOS_LEER"))
):
    repo = ProductRepository(db)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PRODUCTOS_CREAR"))
):
    repo = ProductRepository(db)
    
    if await repo.code_exists(data.codigo):
        raise HTTPException(status_code=400, detail="El código del producto ya existe")
    
    product = Producto(**data.model_dump())
    try:
        created = await repo.create(product)
        return created
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Error de integridad al crear producto")


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PRODUCTOS_ACTUALIZAR"))
):
    repo = ProductRepository(db)
    
    if data.codigo and await repo.code_exists(data.codigo, exclude_id=product_id):
        raise HTTPException(status_code=400, detail="El código del producto ya existe")
    
    product = await repo.update(product_id, **data.model_dump(exclude_unset=True))
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("PRODUCTOS_ELIMINAR"))
):
    repo = ProductRepository(db)
    deleted = await repo.delete(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": "Producto eliminado"}
