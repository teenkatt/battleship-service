"""create games and ship cells tables

Revision ID: c1b6f10262d2
Revises: 
Create Date: 2026-09-17 16:02:52.873655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c1b6f10262d2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "games",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=10), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ship_cells",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("game_id", sa.Uuid(), nullable=False),
        sa.Column("ship_number", sa.Integer(), nullable=False),
        sa.Column("cell", sa.String(length=3), nullable=False),
        sa.Column("is_hit", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("ship_cells")
    op.drop_table("games")
