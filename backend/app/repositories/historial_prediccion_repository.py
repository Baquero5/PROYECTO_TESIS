from sqlalchemy import select, desc, text, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.historial_predicciones import HistorialPrediccion
from typing import List, Optional


class HistorialPrediccionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[HistorialPrediccion]:
        result = await self.db.execute(select(HistorialPrediccion))
        return list(result.scalars().all())

    async def get_with_pagination(self, skip: int = 0, limit: int = 50) -> List[dict]:
        result = await self.db.execute(
            text("""
                SELECT 
                    h.id_historial, h.id_producto, h.id_modelo,
                    h.fecha_prediccion, h.periodo, h.demanda_estimada,
                    h.confianza_min, h.confianza_max, h.horizonte_dias,
                    h.porcentaje_confianza, h.fecha_archivado, h.motivo,
                    p.codigo as codigo_producto, p.nombre as nombre_producto,
                    m.algoritmo as nombre_modelo,
                    s.nombre as nombre_subcategoria,
                    c.nombre as nombre_categoria
                FROM historial_prediccion h
                INNER JOIN producto p ON h.id_producto = p.id_producto
                INNER JOIN modelo_ia m ON h.id_modelo = m.id_modelo
                LEFT JOIN subcategoria s ON p.id_subcategoria = s.id_subcategoria
                LEFT JOIN categoria c ON s.id_categoria = c.id_categoria
                ORDER BY h.fecha_archivado DESC
                LIMIT :limit OFFSET :skip
            """),
            {"limit": limit, "skip": skip}
        )
        return [dict(row._mapping) for row in result.fetchall()]

    async def get_count(self) -> int:
        result = await self.db.execute(text("SELECT COUNT(*) FROM historial_prediccion"))
        return result.scalar()

    async def get_by_product(self, producto_id: int) -> List[HistorialPrediccion]:
        result = await self.db.execute(
            select(HistorialPrediccion)
            .where(HistorialPrediccion.id_producto == producto_id)
            .order_by(desc(HistorialPrediccion.fecha_archivado))
        )
        return list(result.scalars().all())

    async def archivar_por_producto(self, producto_id: int, motivo: str = "REEMPLAZADA", modelo_id: int = None) -> int:
        """Mueve las predicciones actuales de un producto al historial. Opcionalmente filtra por modelo."""
        from app.models.predicciones import Prediccion

        query = select(Prediccion).where(Prediccion.id_producto == producto_id)
        if modelo_id is not None:
            query = query.where(Prediccion.id_modelo == modelo_id)
        
        predicciones = await self.db.execute(query)
        rows = predicciones.scalars().all()

        if not rows:
            return 0

        for pred in rows:
            historial = HistorialPrediccion(
                id_producto=pred.id_producto,
                id_modelo=pred.id_modelo,
                fecha_prediccion=pred.fecha_prediccion,
                periodo=pred.periodo,
                demanda_estimada=pred.demanda_estimada,
                confianza_min=pred.confianza_min,
                confianza_max=pred.confianza_max,
                horizonte_dias=pred.horizonte_dias,
                porcentaje_confianza=pred.porcentaje_confianza,
                motivo=motivo,
            )
            self.db.add(historial)

        await self.db.commit()
        return len(rows)

    async def archivar_lote(self, producto_ids: List[int], motivo: str = "REEMPLAZADA") -> int:
        """Archiva predicciones para múltiples productos."""
        total = 0
        for pid in producto_ids:
            total += await self.archivar_por_producto(pid, motivo)
        return total

    async def delete_by_product(self, producto_id: int) -> int:
        from sqlalchemy import delete
        result = await self.db.execute(
            delete(HistorialPrediccion).where(HistorialPrediccion.id_producto == producto_id)
        )
        await self.db.commit()
        return result.rowcount

    async def archivar_expiradas(self) -> int:
        """Archiva predicciones cuya fecha_prediccion + horizonte_dias ya pasó (expiradas)."""
        from app.models.predicciones import Prediccion
        from datetime import date

        today = date.today()

        result = await self.db.execute(
            text("""
                SELECT id_prediccion, id_producto, id_modelo, fecha_prediccion,
                       periodo, demanda_estimada, confianza_min, confianza_max,
                       horizonte_dias, porcentaje_confianza
                FROM prediccion
                WHERE DATE_ADD(fecha_prediccion, INTERVAL horizonte_dias DAY) < :today
            """),
            {"today": today}
        )
        rows = result.fetchall()

        if not rows:
            return 0

        for row in rows:
            historial = HistorialPrediccion(
                id_producto=row.id_producto,
                id_modelo=row.id_modelo,
                fecha_prediccion=row.fecha_prediccion,
                periodo=row.periodo,
                demanda_estimada=row.demanda_estimada,
                confianza_min=float(row.confianza_min) if row.confianza_min else None,
                confianza_max=float(row.confianza_max) if row.confianza_max else None,
                horizonte_dias=row.horizonte_dias,
                porcentaje_confianza=float(row.porcentaje_confianza) if row.porcentaje_confianza else None,
                motivo="EXPIRADA",
            )
            self.db.add(historial)

        # Eliminar las predicciones expiradas de la tabla activa
        pred_ids = [row.id_prediccion for row in rows]
        placeholders = ", ".join([f":pid_{i}" for i in range(len(pred_ids))])
        params = {f"pid_{i}": pid for i, pid in enumerate(pred_ids)}
        await self.db.execute(
            text(f"DELETE FROM prediccion WHERE id_prediccion IN ({placeholders})"),
            params
        )

        await self.db.commit()
        return len(rows)
