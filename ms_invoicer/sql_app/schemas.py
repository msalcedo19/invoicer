from datetime import datetime
from typing import List, Union
from pydantic import BaseModel


class GlobalBase(BaseModel):
    name: str
    value: str
    created: datetime
    updated: datetime


class GlobalCreate(GlobalBase):
    pass


class Global(GlobalBase):
    id: int

    class Config:
        orm_mode = True


class ServiceBase(BaseModel):
    title: str
    amount: int
    currency: str
    hours: int
    price_unit: float
    file_id: int
    invoice_id: int


class ServiceCreate(ServiceBase):
    pass


class Service(ServiceBase):
    id: int

    class Config:
        orm_mode = True


class BillToBase(BaseModel):
    to: str
    addr: str
    phone: str
    email: str


class BillToCreate(BillToBase):
    pass


class BillTo(BillToBase):
    id: int

    class Config:
        orm_mode = True


class TopInfoBase(BaseModel):
    ti_from: str
    email: str
    addr: str
    phone: str


class TopInfoCreate(TopInfoBase):
    pass


class TopInfo(TopInfoBase):
    id: int

    class Config:
        orm_mode = True


class FileBase(BaseModel):
    s3_xlsx_url: str
    s3_pdf_url: Union[str, None]
    created: datetime
    invoice_id: int
    bill_to_id: int


class FileCreate(FileBase):
    pass


class CustomerBase(BaseModel):
    name: str


class CustomerCreate(CustomerBase):
    pass


class CustomerLite(CustomerBase):
    id: int
    num_invoices: int

    class Config:
        orm_mode = True


class InvoiceBase(BaseModel):
    number_id: int
    reason: str
    tax_1: int
    tax_2: int
    created: datetime
    updated: datetime
    customer_id: int


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceLite(InvoiceBase):
    id: int

    class Config:
        orm_mode = True

class File(FileBase):
    id: int
    bill_to: BillTo
    services: list[Service] = []

    class Config:
        orm_mode = True


class Invoice(InvoiceBase):
    id: int
    files: List[File] = []

    class Config:
        orm_mode = True

class Customer(CustomerBase):
    id: int
    num_invoices: int
    invoices: List[Invoice] = []

    class Config:
        orm_mode = True