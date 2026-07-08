"""add_historial_predicciones

Revision ID: c4d5e6f7a8b9
Revises: a1b2c3d4e5f6
Create Date: 2026-07-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'c4d5e6f7a8b9'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'historial_predicciones',
        sa.Column('id_historial', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('id_producto', sa.Integer(), sa.ForeignKey('productos.id_producto'), nullable=False),
        sa.Column('id_modelo', sa.Integer(), sa.ForeignKey('modelos_ia.id_modelo'), nullable=False),
        sa.Column('fecha_prediccion', sa.Date(), nullable=True),
        sa.Column('periodo', sa.String(20), nullable=True),
        sa.Column('demanda_estimada', sa.Integer(), server_default='0'),
        sa.Column('confianza_min', sa.Numeric(10, 2), nullable=True),
        sa.Column('confianza_max', sa.Numeric(10, 2), nullable=True),
        sa.Column('horizonte_dias', sa.Integer(), server_default='30'),
        sa.Column('porcentaje_confianza', sa.Numeric(5, 2), server_default='95.0'),
        sa.Column('fecha_archivado', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('motivo', sa.String(50), server_default='REEMPLAZADA'),
    )


def downgrade() -> None:
    op.drop_table('historial_predicciones')
