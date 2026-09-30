"""index game lookups

Revision ID: f3c07a15e2d9
Revises: a7d4e93b51c8
Create Date: 2026-09-30 15:42:07.551308

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'f3c07a15e2d9'
down_revision: Union[str, Sequence[str], None] = 'a7d4e93b51c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index("ix_ship_cells_game_id_cell", "ship_cells", ["game_id", "cell"])
    op.create_index("ix_shots_game_id", "shots", ["game_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_shots_game_id", table_name="shots")
    op.drop_index("ix_ship_cells_game_id_cell", table_name="ship_cells")
