from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.venta_repository import VentaRepository
from app.repositories.detalle_venta_repository import DetalleVentaRepository
from app.repositories.inventario_repository import InventarioRepository
from app.schemas.venta import VentaCreate, VentaResponse, DetalleVentaResponse
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/api/ventas", tags=["Ventas"])


@router.get("", response_model=List[VentaResponse])
async def get_ventas(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repo = VentaRepository(db)
    return await repo.get_all(skip, limit)


@router.get("/{venta_id}", response_model=VentaResponse)
async def get_venta(venta_id: int, db: AsyncSession = Depends(get_db)):
    repo = VentaRepository(db)
    venta = await repo.get_by_id(venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    detalles = await repo.get_details(venta_id)
    venta_dict = VentaResponse.model_validate(venta).model_dump()
    venta_dict["detalles"] = [DetalleVentaResponse.model_validate(d) for d in detalles]
    return venta_dict


@router.post("", response_model=VentaResponse, status_code=201)
async def create_venta(data: VentaCreate, db: AsyncSession = Depends(get_db)):
    venta_repo = VentaRepository(db)
    detalle_repo = DetalleVentaRepository(db)
    inventario_repo = InventarioRepository(db)
    
    from app.models.ventas import Venta
    from app.models.detalle_ventas import DetalleVenta
    
    total = sum(d.cantidad * d.precio_unitario for d in data.detalles)
    
    venta = Venta(
        id_usuario=data.id_usuario,
        total=total
    )
    created_venta = await venta_repo.create(venta)
    
    detalles = []
    for d in data.detalles:
        inventario = await inventario_repo.get_by_product(d.id_producto)
        if not inventario or inventario.stock_actual < d.cantidad:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para producto {d.id_producto}")
        
        await inventario_repo.update_stock(d.id_producto, d.cantidad, "SALIDA")
        
        detalle = DetalleVenta(
            id_venta=created_venta.id_venta,
            id_producto=d.id_producto,
            cantidad=d.cantidad,
            precio_unitario=d.precio_unitario,
            subtotal=d.cantidad * d.precio_unitario
        )
        detalles.append(detalle)
    
    await detalle_repo.create_many(detalles)
    
    venta_response = VentaResponse.model_validate(created_venta).model_dump()
    venta_response["detalles"] = [DetalleVentaResponse.model_validate(d) for d in detalles]
    return venta_response


@router.get("/usuario/{usuario_id}", response_model=List[VentaResponse])
async def get_ventas_by_user(usuario_id: int, db: AsyncSession = Depends(get_db)):
    repo = VentaRepository(db)
    return await repo.get_by_user(usuario_id)


class SalesHistoryResponse(BaseModel):
    fecha: str
    cantidad: int
    precio: float


@router.get("/producto/{producto_id}/historial", response_model=List[SalesHistoryResponse])
async def get_sales_history(producto_id: int, days: int = 90, db: AsyncSession = Depends(get_db)):
    repo = VentaRepository(db)
    return await repo.get_sales_history_by_product(producto_id, days)
