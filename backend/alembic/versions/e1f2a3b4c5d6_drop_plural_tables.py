"""drop_plural_tables

Revision ID: e1f2a3b4c5d6
Revises: d11ac08292f8
Create Date: 2026-07-14

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, None] = 'd11ac08292f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Eliminar tablas residuales en plural que no usa el sistema
    # Orden correcto: primero tablas dependientes, luego las principales
    op.execute("SET FOREIGN_KEY_CHECKS = 0")

    tables_to_drop = [
        'historial_predicciones',
        'detalle_ventas',
        'predicciones',
        'parametros_inventario',
        'movimientos_inventario',
        'inventarios',
        'alertas',
        'usuarios',
        'productos',
        'modelos_ia',
        'proveedores',
        'subcategorias',
        'categorias',
        'ventas',
        'reabastecimientos',
    ]

    for table in tables_to_drop:
        op.execute(f"DROP TABLE IF EXISTS {table}")

    op.execute("SET FOREIGN_KEY_CHECKS = 1")


def downgrade() -> None:
    pass
