"""template table

Revision ID: c710ef4198dd
Revises: a4165cb2a1eb
Create Date: 2023-06-01 10:11:24.115114

"""
from alembic import op
import sqlalchemy as sa
from ms_invoicer.sql_app.models import Template, User


# revision identifiers, used by Alembic.
revision = "c710ef4198dd"
down_revision = "a4165cb2a1eb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        Template.__tablename__,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("created", sa.DateTime, nullable=False),
        sa.Column("updated", sa.DateTime, nullable=False),
    )
    op.create_foreign_key(
        "fk_user_id",
        Template.__tablename__,
        User.__tablename__,
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    pass
