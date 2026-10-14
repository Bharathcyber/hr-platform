
"""increase role grade length

Revision ID: 40545a6339e4
Revises: fb183e4553d5
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "40545a6339e4"
down_revision: Union[str, Sequence[str], None] = "fb183e4553d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "roles",
        "grade",
        existing_type=sa.VARCHAR(length=20),
        type_=sa.String(length=100),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "roles",
        "grade",
        existing_type=sa.String(length=100),
        type_=sa.VARCHAR(length=20),
        existing_nullable=True,
    )
