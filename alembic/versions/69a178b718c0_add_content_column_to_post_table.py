"""add content column to post table

Revision ID: 69a178b718c0
Revises: e427806f59d3
Create Date: 2023-04-14 00:06:09.492120

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "69a178b718c0"
down_revision = "e427806f59d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("content", sa.String(1000), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column("posts", "content")
    pass
