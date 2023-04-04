from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Double
from sqlalchemy.orm import relationship

from ms_invoicer.sql_app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    invoices = relationship("Invoice")

    @property
    def num_invoices(self):
        return len(self.invoices)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    number_id = Column(Integer)
    reason = Column(String)
    tax_1 = Column(Integer)
    tax_2 = Column(Integer)
    created = Column(DateTime)
    updated = Column(DateTime)
    customer_id = Column(Integer, ForeignKey("customers.id"))

    customer = relationship("Customer", back_populates="invoices", uselist=False)
    files = relationship("File")


class BillTo(Base):
    __tablename__ = "billto"

    id = Column(Integer, primary_key=True, index=True)
    to = Column(String)
    addr = Column(String)
    phone = Column(String)
    email = Column(String)


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    amount = Column(Integer)
    currency = Column(String)
    hours = Column(Integer)
    price_unit = Column(Double)
    file_id = Column(Integer, ForeignKey("files.id"))
    invoice_id = Column(Integer, ForeignKey("invoices.id"))


class TopInfo(Base):
    __tablename__ = "topinfos"

    id = Column(Integer, primary_key=True, index=True)
    ti_from = Column(String)
    addr = Column(String)
    email = Column(String)
    phone = Column(String)


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    s3_xlsx_url = Column(String)
    s3_pdf_url = Column(String)
    created = Column(DateTime)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    bill_to_id = Column(Integer, ForeignKey("billto.id"))

    bill_to = relationship("BillTo", uselist=False)
    services = relationship("Service")


class Globals(Base):
    __tablename__ = "global"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    value = Column(String)
    created = Column(DateTime)
    updated = Column(DateTime)
