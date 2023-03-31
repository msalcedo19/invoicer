"""create costumer table

Revision ID: a4165cb2a1eb
Revises: 
Create Date: 2023-02-15 22:17:41.098830

"""
from datetime import datetime
from alembic import op
import sqlalchemy as sa
from ms_invoicer.sql_app.models import (
    Customer,
    Contract,
    Globals,
    TopInfo,
    Invoice,
    BillTo,
    Service,
    File,
)

# revision identifiers, used by Alembic.
revision = "a4165cb2a1eb"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        Customer.__tablename__,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
    )

    op.create_table(
        Contract.__tablename__,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("price_unit", sa.Integer, nullable=True),
        sa.Column("customer_id", sa.Integer, nullable=False),
    )
    op.create_foreign_key(
        "fk_customer_id",
        Contract.__tablename__,
        Customer.__tablename__,
        ["customer_id"],
        ["id"],
    )

    top_info_table = op.create_table(
        TopInfo.__tablename__,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ti_from", sa.String(128), nullable=False),
        sa.Column("addr", sa.String(128), nullable=False),
        sa.Column("email", sa.String(128), nullable=False),
        sa.Column("phone", sa.String(50), nullable=False),
    )
    op.bulk_insert(
        top_info_table,
        [
            {
                "ti_from": "John Doe",
                "addr": "5655 rue Bellerive, Brossard,Qc,J4Z 3C9",
                "email": "john@example.com",
                "phone": "450-888 4035",
            },
        ],
    )

    op.create_table(
        Invoice.__tablename__,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("number_id", sa.Integer, nullable=False),
        sa.Column("reason", sa.String(50), nullable=False),
        sa.Column("tax_1", sa.Integer, nullable=False),
        sa.Column("tax_2", sa.Integer, nullable=False),
        sa.Column("created", sa.DateTime, nullable=False),
        sa.Column("updated", sa.DateTime, nullable=False),
        sa.Column("contract_id", sa.Integer, nullable=False),
        sa.Column("bill_to_id", sa.Integer, nullable=False),
    )
    op.create_foreign_key(
        "fk_customer_id",
        Invoice.__tablename__,
        Contract.__tablename__,
        ["contract_id"],
        ["id"],
    )

    op.create_table(
        BillTo.__tablename__,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("to", sa.String(128), nullable=False),
        sa.Column("addr", sa.String(128), nullable=False),
        sa.Column("phone", sa.String(50), nullable=False),
    )
    op.create_foreign_key(
        "fk_bill_to_id",
        Invoice.__tablename__,
        BillTo.__tablename__,
        ["bill_to_id"],
        ["id"],
    )

    op.create_table(
        File.__tablename__,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("s3_xlsx_url", sa.String(256), nullable=False),
        sa.Column("s3_pdf_url", sa.String(256), nullable=True),
        sa.Column("created", sa.DateTime, nullable=False),
        sa.Column("invoice_id", sa.Integer, nullable=True),
    )
    op.create_foreign_key(
        "fk_invoice_id",
        File.__tablename__,
        Invoice.__tablename__,
        ["invoice_id"],
        ["id"],
    )

    op.create_table(
        Service.__tablename__,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(64), nullable=False),
        sa.Column("amount", sa.Integer, nullable=False),
        sa.Column("currency", sa.String(32), nullable=False),
        sa.Column("hours", sa.Integer, nullable=False),
        sa.Column("price_unit", sa.Integer, nullable=False),
        sa.Column("file_id", sa.Integer, nullable=True),
    )
    op.create_foreign_key(
        "fk_file_id",
        Service.__tablename__,
        File.__tablename__,
        ["file_id"],
        ["id"],
    )

    global_table = op.create_table(
        Globals.__tablename__,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("value", sa.String(128), nullable=False),
        sa.Column("created", sa.DateTime, nullable=False),
        sa.Column("updated", sa.DateTime, nullable=False),
    )
    op.bulk_insert(
        global_table,
        [
            {
                "name": "TPS 709597603 RT0001",
                "value": "10",
                "created": datetime.now(),
                "updated": datetime.now(),
            },
            {
                "name": "TVQ1229793019 TQ0001",
                "value": "5",
                "created": datetime.now(),
                "updated": datetime.now(),
            },
        ],
    )


def downgrade() -> None:
    op.drop_table(Globals.__tablename__)
    op.drop_table(Service.__tablename__)
    op.drop_table(File.__tablename__)
    op.drop_table(Invoice.__tablename__)
    op.drop_table(BillTo.__tablename__)
    op.drop_table(TopInfo.__tablename__)
    op.drop_table(Contract.__tablename__)
    op.drop_table(Customer.__tablename__)
