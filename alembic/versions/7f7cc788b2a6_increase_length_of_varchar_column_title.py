"""Increase length of VARCHAR column title

Revision ID: 7f7cc788b2a6
Revises: 4bdf7dec46bf
Create Date: 2024-01-03 16:25:41.962067

"""
from alembic import op
import sqlalchemy as sa

from ms_invoicer.sql_app.models import Service


# revision identifiers, used by Alembic.
revision = '7f7cc788b2a6'
down_revision = '4bdf7dec46bf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(Service.__tablename__, 'title', 
               type_=sa.String(length=255), 
               existing_type=sa.String(length=64),
               existing_nullable=False)


def downgrade() -> None:
    pass
