"""Add pages_xlsx column in File

Revision ID: ded5cccdcb92
Revises: 81efd01d0d73
Create Date: 2023-11-04 12:12:45.664335

"""
from alembic import op
import sqlalchemy as sa

from ms_invoicer.sql_app.models import File


# revision identifiers, used by Alembic.
revision = 'ded5cccdcb92'
down_revision = '81efd01d0d73'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(File.__tablename__, sa.Column('pages_xlsx', sa.String, nullable=True))


def downgrade() -> None:
    pass
