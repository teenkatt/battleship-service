"""create shots table

Revision ID: a7d4e93b51c8
Revises: c1b6f10262d2
Create Date: 2026-09-30 12:10:44.318902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a7d4e93b51c8'
down_revision: Union[str, Sequence[str], None] = 'c1b6f10262d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "shots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("game_id", sa.Uuid(), nullable=False),
        sa.Column("cell", sa.String(length=3), nullable=False),
        sa.Column("result", sa.String(length=6), nullable=True),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("shots")
