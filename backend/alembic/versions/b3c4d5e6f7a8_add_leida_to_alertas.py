"""add_leida_to_alertas

Revision ID: b3c4d5e6f7a8
Revises: a1b2c3d4e5f6
Create Date: 2026-06-26
"""
from alembic import op
import sqlalchemy as sa

revision = 'b3c4d5e6f7a8'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('alertas', sa.Column('leida', sa.Boolean(), server_default='false'))


def downgrade() -> None:
    op.drop_column('alertas', 'leida')
