"""taxes nullable

Revision ID: 81efd01d0d73
Revises: b0e46e577481
Create Date: 2023-09-09 20:36:26.163360

"""
from alembic import op
import sqlalchemy as sa

from ms_invoicer.sql_app.models import Invoice


# revision identifiers, used by Alembic.
revision = '81efd01d0d73'
down_revision = 'b0e46e577481'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(Invoice.__tablename__, "tax_1", nullable=False)
    op.alter_column(Invoice.__tablename__, "tax_2", nullable=False)
    op.add_column(Invoice.__tablename__, sa.Column('with_taxes', sa.Boolean))


def downgrade() -> None:
    op.drop_column(Invoice.__tablename__, "with_taxes")
