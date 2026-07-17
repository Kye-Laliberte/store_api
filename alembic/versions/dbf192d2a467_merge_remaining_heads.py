"""merge remaining heads

Revision ID: dbf192d2a467
Revises: 09b99f6c2d52, 7672737d42da, 988d64492952
Create Date: 2026-07-17 13:47:57.912156
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'dbf192d2a467'
down_revision = ('09b99f6c2d52', '7672737d42da', '988d64492952')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass