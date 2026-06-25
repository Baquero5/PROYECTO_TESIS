"""add_r2_to_modelos_ia

Revision ID: a1b2c3d4e5f6
Revises: f637358567b0
Create Date: 2026-06-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'a1b2c3d4e5f6'
down_revision = 'f637358567b0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('modelos_ia', sa.Column('r2', sa.Numeric(10, 4), nullable=True))


def downgrade() -> None:
    op.drop_column('modelos_ia', 'r2')
