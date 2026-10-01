"""add admin flag to users

Revision ID: a38b4f1c2d90
Revises: caca135a4659
"""

from alembic import op
import sqlalchemy as sa


revision = "a38b4f1c2d90"
down_revision = "caca135a4659"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.alter_column("users", "is_admin", server_default=None)


def downgrade():
    op.drop_column("users", "is_admin")