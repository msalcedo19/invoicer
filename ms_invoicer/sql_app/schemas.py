from datetime import datetime
from typing import Union
from pydantic import BaseModel


class ServiceBase(BaseModel):
    title: str
    amount: int
    currency: str
    hours: int
    price_unit: int


class ServiceCreate(ServiceBase):
    pass


class Service(ServiceBase):
    id: int
    invoice_id: Union[int, None]

    class Config:
        orm_mode = True


class BillToBase(BaseModel):
    to: str
    addr: str
    phone: str


class BillToCreate(BillToBase):
    pass


class BillTo(BillToBase):
    id: int
    invoice_id: Union[int, None]

    class Config:
        orm_mode = True


class TopInfoBase(BaseModel):
    to: str
    addr: int
    phone: str


class TopInfoCreate(TopInfoBase):
    pass


class TopInfo(TopInfoBase):
    id: int
    customer_id: int

    class Config:
        orm_mode = True


class FileBase(BaseModel):
    s3_xlsx_url: str
    s3_pdf_url: str
    created: datetime


class FileCreate(FileBase):
    pass


class File(FileBase):
    id: int
    invoice_id: Union[int, None] = None

    class Config:
        orm_mode = True


class InvoiceBase(BaseModel):
    number: int
    reason: str
    subtotal: int
    total: int
    created: datetime
    updated: datetime
    customer_id: int


class InvoiceCreate(InvoiceBase):
    pass


class Invoice(InvoiceBase):
    id: int
    bill_to: Union[BillTo, None] = None
    file: Union[File, None] = None
    services: list[Service] = []

    class Config:
        orm_mode = True


class CustomerBase(BaseModel):
    name: str
    tax1: int
    tax2: int
    price_unit: int


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase):
    id: int
    top_info: Union[TopInfo, None] = None
    invoices: list[Invoice] = []

    class Config:
        orm_mode = True
