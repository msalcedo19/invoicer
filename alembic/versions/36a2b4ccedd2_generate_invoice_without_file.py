"""generate invoice without file

Revision ID: 36a2b4ccedd2
Revises: c710ef4198dd
Create Date: 2023-07-19 22:44:45.654905

"""
from alembic import op
import sqlalchemy as sa

from ms_invoicer.sql_app.models import File


# revision identifiers, used by Alembic.
revision = '36a2b4ccedd2'
down_revision = 'c710ef4198dd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(File.__tablename__, "s3_xlsx_url", nullable=True)


def downgrade() -> None:
    pass
