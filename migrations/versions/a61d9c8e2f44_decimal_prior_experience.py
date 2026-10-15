
"""Change prior experience years to decimal.

Revision ID: a61d9c8e2f44
Revises: b3ef74523c36
"""

from alembic import op
import sqlalchemy as sa


revision = "a61d9c8e2f44"
down_revision = "b3ef74523c36"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "employees",
        "prior_experience_years",
        existing_type=sa.Integer(),
        type_=sa.Numeric(5, 2),
        existing_nullable=False,
        existing_server_default=sa.text("0"),
        postgresql_using="prior_experience_years::numeric(5,2)",
    )


def downgrade():
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM employees
                WHERE prior_experience_years <> trunc(prior_experience_years)
            ) THEN
                RAISE EXCEPTION
                    'Cannot downgrade: prior_experience_years contains fractional values.';
            END IF;
        END $$;
        """
    )

    op.alter_column(
        "employees",
        "prior_experience_years",
        existing_type=sa.Numeric(5, 2),
        type_=sa.Integer(),
        existing_nullable=False,
        existing_server_default=sa.text("0"),
        postgresql_using="prior_experience_years::integer",
    )
