from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.subcategorias import Subcategoria
from app.models.categorias import Categoria
from typing import List, Optional


class SubcategoriaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[dict]:
        result = await self.db.execute(
            select(Subcategoria, Categoria.nombre.label("nombre_categoria"))
            .join(Categoria, Subcategoria.id_categoria == Categoria.id_categoria)
        )
        rows = result.all()
        return [
            {
                "id_subcategoria": s.id_subcategoria,
                "id_categoria": s.id_categoria,
                "nombre": s.nombre,
                "descripcion": s.descripcion,
                "nombre_categoria": nombre_categoria,
            }
            for s, nombre_categoria in rows
        ]

    async def get_by_categoria(self, categoria_id: int) -> List[dict]:
        result = await self.db.execute(
            select(Subcategoria, Categoria.nombre.label("nombre_categoria"))
            .join(Categoria, Subcategoria.id_categoria == Categoria.id_categoria)
            .where(Subcategoria.id_categoria == categoria_id)
        )
        rows = result.all()
        return [
            {
                "id_subcategoria": s.id_subcategoria,
                "id_categoria": s.id_categoria,
                "nombre": s.nombre,
                "descripcion": s.descripcion,
                "nombre_categoria": nombre_categoria,
            }
            for s, nombre_categoria in rows
        ]

    async def get_by_id(self, subcategoria_id: int) -> Optional[dict]:
        result = await self.db.execute(
            select(Subcategoria, Categoria.nombre.label("nombre_categoria"))
            .join(Categoria, Subcategoria.id_categoria == Categoria.id_categoria)
            .where(Subcategoria.id_subcategoria == subcategoria_id)
        )
        row = result.first()
        if not row:
            return None
        s, nombre_categoria = row
        return {
            "id_subcategoria": s.id_subcategoria,
            "id_categoria": s.id_categoria,
            "nombre": s.nombre,
            "descripcion": s.descripcion,
            "nombre_categoria": nombre_categoria,
        }

    async def create(self, subcategoria: Subcategoria) -> dict:
        self.db.add(subcategoria)
        await self.db.commit()
        await self.db.refresh(subcategoria)
        result = await self.db.execute(
            select(Categoria.nombre).where(Categoria.id_categoria == subcategoria.id_categoria)
        )
        nombre_categoria = result.scalar_one_or_none()
        return {
            "id_subcategoria": subcategoria.id_subcategoria,
            "id_categoria": subcategoria.id_categoria,
            "nombre": subcategoria.nombre,
            "descripcion": subcategoria.descripcion,
            "nombre_categoria": nombre_categoria,
        }

    async def update(self, subcategoria_id: int, **kwargs) -> Optional[dict]:
        result = await self.db.execute(
            select(Subcategoria).where(Subcategoria.id_subcategoria == subcategoria_id)
        )
        sub = result.scalar_one_or_none()
        if not sub:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(sub, key, value)
        await self.db.commit()
        await self.db.refresh(sub)
        result = await self.db.execute(
            select(Categoria.nombre).where(Categoria.id_categoria == sub.id_categoria)
        )
        nombre_categoria = result.scalar_one_or_none()
        return {
            "id_subcategoria": sub.id_subcategoria,
            "id_categoria": sub.id_categoria,
            "nombre": sub.nombre,
            "descripcion": sub.descripcion,
            "nombre_categoria": nombre_categoria,
        }

    async def delete(self, subcategoria_id: int) -> bool:
        result = await self.db.execute(
            select(Subcategoria).where(Subcategoria.id_subcategoria == subcategoria_id)
        )
        sub = result.scalar_one_or_none()
        if not sub:
            return False
        await self.db.delete(sub)
        await self.db.commit()
        return True
