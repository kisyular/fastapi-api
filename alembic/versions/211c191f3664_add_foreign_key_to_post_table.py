"""add foreign-key to post table

Revision ID: 211c191f3664
Revises: 421e8b6ef010
Create Date: 2023-04-14 12:37:34.050266

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "211c191f3664"
down_revision = "421e8b6ef010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "posts",
        sa.Column("owner_id", sa.Integer, nullable=False),
    )
    op.create_foreign_key(
        "posts_users_fk",
        source_table="posts",
        referent_table="users",
        local_cols=["owner_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )
    pass


def downgrade() -> None:
    op.drop_constraint("posts_users_fk", table_name="posts", type_="foreignkey")
    op.drop_column("posts", "owner_id")
    pass
