"""add the remaining columns to the post table

Revision ID: 52598a9bac54
Revises: 211c191f3664
Create Date: 2023-04-14 12:46:18.577848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "52598a9bac54"
down_revision = "211c191f3664"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "posts",
        sa.Column("published", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column("posts", sa.Column("category", sa.String(), nullable=False))
    op.add_column(
        "posts",
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    pass


def downgrade() -> None:
    op.drop_column("posts", "published")
    op.drop_column("posts", "category")
    op.drop_column("posts", "created_at")
    pass
