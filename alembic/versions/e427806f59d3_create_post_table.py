"""create post table

Revision ID: e427806f59d3
Revises: 
Create Date: 2023-04-13 23:39:18.626910

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e427806f59d3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer, primary_key=True, nullable=False),
        sa.Column("title", sa.String(100), nullable=False),
    )
    pass


def downgrade() -> None:
    pass
