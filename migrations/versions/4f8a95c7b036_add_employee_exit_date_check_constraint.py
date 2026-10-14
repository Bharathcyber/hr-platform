"""Add employee exit date check constraint."""

from alembic import op

# Revision identifiers
revision = "4f8a95c7b036"
down_revision = "0f4c168deb1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_employees_exit_date_after_hire_date",
        "employees",
        "exit_date IS NULL OR hire_date IS NULL OR exit_date >= hire_date",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_employees_exit_date_after_hire_date",
        "employees",
        type_="check",
    )
