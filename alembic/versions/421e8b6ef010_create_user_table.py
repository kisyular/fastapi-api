"""create user table

Revision ID: 421e8b6ef010
Revises: 69a178b718c0
Create Date: 2023-04-14 12:27:14.270873

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "421e8b6ef010"
down_revision = "69a178b718c0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    pass


def downgrade() -> None:
    op.drop_table("users")
    pass
