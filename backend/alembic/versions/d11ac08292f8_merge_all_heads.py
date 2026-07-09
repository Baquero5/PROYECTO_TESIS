"""merge_all_heads

Revision ID: d11ac08292f8
Revises: b3c4d5e6f7a8, c4d5e6f7a8b9, clean_old_tables
Create Date: 2026-07-08 18:30:11.254318

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd11ac08292f8'
down_revision: Union[str, None] = ('b3c4d5e6f7a8', 'c4d5e6f7a8b9', 'clean_old_tables')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
