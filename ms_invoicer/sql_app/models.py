from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from ms_invoicer.sql_app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price_unit = Column(Integer)

    invoices = relationship("Invoice", back_populates="customer")
    top_info = relationship("TopInfo", back_populates="customer", uselist=False)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    reason = Column(String)
    tax_1 = Column(Integer)
    tax_2 = Column(Integer)
    created = Column(DateTime)
    updated = Column(DateTime)
    customer_id = Column(Integer, ForeignKey("customers.id"))

    customer = relationship("Customer", back_populates="invoices", uselist=False)
    bill_to = relationship("BillTo", back_populates="invoice", uselist=False)
    files = relationship("File", back_populates="invoice")


class BillTo(Base):
    __tablename__ = "billto"

    id = Column(Integer, primary_key=True, index=True)
    to = Column(String)
    addr = Column(String)
    phone = Column(String)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))

    invoice = relationship("Invoice", back_populates="bill_to")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    amount = Column(Integer)
    currency = Column(String)
    hours = Column(Integer)
    price_unit = Column(Integer)
    file_id = Column(Integer, ForeignKey("files.id"))

    file = relationship("File", back_populates="services", uselist=False)


class TopInfo(Base):
    __tablename__ = "topinfos"

    id = Column(Integer, primary_key=True, index=True)
    addr = Column(String)
    phone = Column(String)
    customer_id = Column(Integer, ForeignKey("customers.id"))

    customer = relationship("Customer", back_populates="top_info")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    s3_xlsx_url = Column(String)
    s3_pdf_url = Column(String)
    created = Column(DateTime)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))

    services = relationship("Service", back_populates="file")
    invoice = relationship("Invoice", back_populates="files", uselist=False)


class Globals(Base):
    __tablename__ = "global"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    value = Column(String)
    created = Column(DateTime)
