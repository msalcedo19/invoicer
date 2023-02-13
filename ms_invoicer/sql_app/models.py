from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tax1 = Column(Integer)
    tax2 = Column(Integer)
    price_unit = Column(Integer)
    top_info_id = Column(Integer, ForeignKey("topinfos.id"))

    invoices = relationship("Invoice", back_populates="customer")
    top_info = relationship("TopInfo", back_populates="customer")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, index=True)
    reason = Column(String)
    subtotal = Column(Integer)
    total = Column(Integer)
    created = Column(DateTime)
    updated = Column(DateTime)
    customer_id = Column(Integer, ForeignKey("customers.id"))

    customer = relationship("Customer", back_populates="invoices")
    bill_to = relationship("BillTo", back_populates="invoices")
    services = relationship("Service", back_populates="services")
    top_info = relationship("TopInfo", back_populates="topinfos")
    file = relationship("TopInfo", back_populates="topinfos")


class BillTo(Base):
    __tablename__ = "billto"

    id = Column(Integer, primary_key=True, index=True)
    to = Column(String)
    addr = Column(String)
    phone = Column(String)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))

    invoices = relationship("Invoice", back_populates="bill_to")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    amount = Column(Integer)
    currency = Column(String)
    hours = Column(Integer)
    price_unit = Column(Integer)


class TopInfo(Base):
    __tablename__ = "topinfos"

    id = Column(Integer, primary_key=True, index=True)
    addr = Column(String)
    phone = Column(String)

    customer = relationship("Customer", back_populates="top_info")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created = Column(DateTime)
