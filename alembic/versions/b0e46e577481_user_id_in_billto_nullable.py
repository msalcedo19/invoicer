"""user_id in billto nullable

Revision ID: b0e46e577481
Revises: 36a2b4ccedd2
Create Date: 2023-08-04 19:56:49.672563

"""
from alembic import op
import sqlalchemy as sa

from ms_invoicer.sql_app.models import BillTo

# revision identifiers, used by Alembic.
revision = 'b0e46e577481'
down_revision = '36a2b4ccedd2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(BillTo.__tablename__, "user_id", nullable=True)


def downgrade() -> None:
    pass
