from datetime import datetime
from typing import Union
from pydantic import BaseModel


class GlobalBase(BaseModel):
    name: str
    value: str
    created: datetime


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
    price_unit: int
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
    s3_pdf_url: Union[str , None]
    created: datetime
    invoice_id: int


class FileCreate(FileBase):
    pass


class CustomerBase(BaseModel):
    name: str
    price_unit: int


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase):
    id: int
    top_info: Union[TopInfo, None] = None

    class Config:
        orm_mode = True


class InvoiceBase(BaseModel):
    reason: str
    subtotal: int # TODO: Verificar si es necesario vs total...
    tax_1: int
    tax_2: int
    created: datetime
    updated: datetime
    customer_id: int


class InvoiceCreate(InvoiceBase):
    pass


class Invoice(InvoiceBase):
    id: int
    bill_to: Union[BillTo, None] = None
    services: list[Service] = []
    customer: Customer

    class Config:
        orm_mode = True

class File(FileBase):
    id: int
    invoice: Invoice

    class Config:
        orm_mode = True