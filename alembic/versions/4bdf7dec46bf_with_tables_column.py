"""with_tables column

Revision ID: 4bdf7dec46bf
Revises: ded5cccdcb92
Create Date: 2023-12-10 20:17:01.760803

"""
from alembic import op
import sqlalchemy as sa

from ms_invoicer.sql_app.models import Invoice

# revision identifiers, used by Alembic.
revision = '4bdf7dec46bf'
down_revision = 'ded5cccdcb92'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(Invoice.__tablename__, sa.Column('with_tables', sa.Boolean))


def downgrade() -> None:
    op.drop_column(Invoice.__tablename__, "with_tables")
