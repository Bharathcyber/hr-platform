
"""add employee manager and full name indexes

Revision ID: cceba3ba5784
Revises: 40545a6339e4
Create Date: 2026-10-14 17:50:14.145688
"""

from typing import Sequence, Union

from alembic import op

# Revision identifiers used by Alembic.
revision: str = "cceba3ba5784"
down_revision: Union[str, Sequence[str], None] = "40545a6339e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the employee manager and full-name indexes."""
    op.create_index(
        "idx_employees_full_name",
        "employees",
        ["full_name"],
        unique=False,
    )
    op.create_index(
        "idx_employees_manager_id",
        "employees",
        ["manager_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the employee manager and full-name indexes."""
    op.drop_index("idx_employees_manager_id", table_name="employees")
    op.drop_index("idx_employees_full_name", table_name="employees")
