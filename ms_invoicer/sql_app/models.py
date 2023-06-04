from sqlalchemy import Column, DateTime, Double, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ms_invoicer.sql_app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("invoicer_user.id"), index=True)

    invoices = relationship("Invoice")

    @property
    def num_invoices(self):
        return len(self.invoices)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    number_id = Column(Integer)
    reason = Column(String)
    tax_1 = Column(Double)
    tax_2 = Column(Double)
    created = Column(DateTime)
    updated = Column(DateTime)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    user_id = Column(Integer, ForeignKey("invoicer_user.id"), index=True)

    customer = relationship("Customer", back_populates="invoices", uselist=False)
    files = relationship("File")


class BillTo(Base):
    __tablename__ = "billto"

    id = Column(Integer, primary_key=True, index=True)
    to = Column(String)
    addr = Column(String)
    phone = Column(String)
    email = Column(String)
    user_id = Column(Integer, ForeignKey("invoicer_user.id"), index=True)


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    amount = Column(Double)
    currency = Column(String)
    hours = Column(Double)
    price_unit = Column(Double)
    file_id = Column(Integer, ForeignKey("files.id"))
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    user_id = Column(Integer, ForeignKey("invoicer_user.id"))


class TopInfo(Base):
    __tablename__ = "topinfos"

    id = Column(Integer, primary_key=True, index=True)
    ti_from = Column(String)
    addr = Column(String)
    email = Column(String)
    phone = Column(String)
    user_id = Column(Integer, ForeignKey("invoicer_user.id"), index=True)


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    s3_xlsx_url = Column(String)
    s3_pdf_url = Column(String)
    created = Column(DateTime)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    bill_to_id = Column(Integer, ForeignKey("billto.id"))
    user_id = Column(Integer, ForeignKey("invoicer_user.id"), index=True)

    bill_to = relationship("BillTo", uselist=False)
    services = relationship("Service")


class Globals(Base):
    __tablename__ = "global"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(Integer)
    name = Column(String, index=True)
    value = Column(String)
    created = Column(DateTime)
    updated = Column(DateTime)
    user_id = Column(Integer, ForeignKey("invoicer_user.id"), index=True)


class User(Base):
    __tablename__ = "invoicer_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    hashpass = Column(String)
    created = Column(DateTime)
    updated = Column(DateTime)


class Template(Base):
    __tablename__ = "template"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("invoicer_user.id"), nullable=True)
    created = Column(DateTime)
    updated = Column(DateTime)
