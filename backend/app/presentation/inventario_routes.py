from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.inventario_repository import InventarioRepository
from app.repositories.movimiento_inventario_repository import MovimientoInventarioRepository
from app.schemas.inventario import InventarioCreate, InventarioUpdate, InventarioResponse, StockUpdate
from app.schemas.movimiento_inventario import MovimientoInventarioCreate, MovimientoInventarioResponse
from app.models.inventarios import Inventario
from app.models.movimientos_inventario import MovimientoInventario
from app.services.auth_service import require_permission
from typing import List

router = APIRouter(prefix="/api/inventario", tags=["Inventario"])


@router.get("", response_model=List[InventarioResponse])
async def get_inventario(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("INVENTARIO_LEER"))
):
    repo = InventarioRepository(db)
    return await repo.get_all()


@router.get("/bajo-stock", response_model=List[InventarioResponse])
async def get_low_stock(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("INVENTARIO_LEER"))
):
    repo = InventarioRepository(db)
    return await repo.get_low_stock()


@router.get("/{inventario_id}", response_model=InventarioResponse)
async def get_inventario_by_id(
    inventario_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("INVENTARIO_LEER"))
):
    repo = InventarioRepository(db)
    inventario = await repo.get_by_id(inventario_id)
    if not inventario:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")
    return inventario


@router.get("/producto/{producto_id}", response_model=InventarioResponse)
async def get_inventario_by_product(
    producto_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("INVENTARIO_LEER"))
):
    repo = InventarioRepository(db)
    inventario = await repo.get_by_product(producto_id)
    if not inventario:
        raise HTTPException(status_code=404, detail="Inventario no encontrado para este producto")
    return inventario


@router.post("", response_model=InventarioResponse, status_code=201)
async def create_inventario(
    data: InventarioCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("INVENTARIO_CREAR"))
):
    repo = InventarioRepository(db)
    if await repo.get_by_product(data.id_producto):
        raise HTTPException(status_code=400, detail="Ya existe inventario para este producto")
    inventario = Inventario(**data.model_dump())
    return await repo.create(inventario)


@router.put("/{inventario_id}", response_model=InventarioResponse)
async def update_inventario(
    inventario_id: int,
    data: InventarioUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("INVENTARIO_ACTUALIZAR"))
):
    repo = InventarioRepository(db)
    inventario = await repo.update(inventario_id, **data.model_dump(exclude_unset=True))
    if not inventario:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")
    return inventario


@router.post("/producto/{producto_id}/movimiento", response_model=MovimientoInventarioResponse)
async def create_movimiento(
    producto_id: int,
    data: StockUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_permission("INVENTARIO_CREAR"))
):
    inventario_repo = InventarioRepository(db)
    movimiento_repo = MovimientoInventarioRepository(db)
    
    inventario = await inventario_repo.get_by_product(producto_id)
    if not inventario:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")
    
    if data.tipo not in ["ENTRADA", "SALIDA"]:
        raise HTTPException(status_code=400, detail="Tipo debe ser ENTRADA o SALIDA")
    
    if data.tipo == "SALIDA" and inventario.stock_actual < data.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")
    
    await inventario_repo.update_stock(producto_id, data.cantidad, data.tipo)
    
    movimiento = MovimientoInventario(
        id_producto=producto_id,
        tipo_movimiento=data.tipo,
        cantidad=data.cantidad,
        observacion=data.observacion
    )
    return await movimiento_repo.create(movimiento)
