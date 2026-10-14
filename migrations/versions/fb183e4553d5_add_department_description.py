
"""add department description

Revision ID: fb183e4553d5
Revises: d9345a30805c
Create Date: 2026-10-14 15:50:38.624482
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "fb183e4553d5"
down_revision: Union[str, Sequence[str], None] = "d9345a30805c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "departments",
        sa.Column("description", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("departments", "description")
