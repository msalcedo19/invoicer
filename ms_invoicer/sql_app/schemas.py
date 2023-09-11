from datetime import datetime
from typing import List, Union, Optional

from pydantic import BaseModel


# USER -------------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class UserBase(BaseModel):
    username: str
    hashpass: str
    created: datetime
    updated: datetime


class UserCreate(UserBase):
    pass


class UserAuthenticate(BaseModel):
    username: str
    password: str


class UserAuthenticateResponse(BaseModel):
    username: str
    token: str


class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


# Template -------------------------------------------------------------
class TemplateBase(BaseModel):
    name: str
    created: datetime
    updated: datetime


class TemplateCreate(TemplateBase):
    user_id: int


class Template(TemplateBase):
    id: int

    class Config:
        orm_mode = True


# Global -------------------------------------------------------------
class GlobalBase(BaseModel):
    identifier: int
    name: str
    value: str
    created: datetime
    updated: datetime


class GlobalCreate(GlobalBase):
    user_id: int


class Global(GlobalBase):
    id: int

    class Config:
        orm_mode = True


# SERVICE -------------------------------------------------------------
class ServiceBase(BaseModel):
    title: str
    amount: int
    currency: str
    hours: float
    price_unit: float
    file_id: int
    invoice_id: int


class ServiceCreate(ServiceBase):
    user_id: int

class ServiceCreateNoFile(BaseModel):
    title: str
    amount: int
    currency: str
    hours: float
    price_unit: float

class Service(ServiceBase):
    id: int

    class Config:
        orm_mode = True


# BILLTO -------------------------------------------------------------
class BillToBase(BaseModel):
    to: str
    addr: str
    phone: str
    email: str


class BillToCreate(BillToBase):
    user_id: int


class BillTo(BillToBase):
    id: int

    class Config:
        orm_mode = True


# TOPINFO -------------------------------------------------------------
class TopInfoBase(BaseModel):
    ti_from: str
    email: str
    addr: str
    phone: str


class TopInfoCreate(TopInfoBase):
    user_id: int


class TopInfo(TopInfoBase):
    id: int

    class Config:
        orm_mode = True


# FILE -------------------------------------------------------------
class FileBase(BaseModel):
    s3_xlsx_url: Union[str, None]
    s3_pdf_url: Union[str, None]
    created: datetime
    invoice_id: int
    bill_to_id: int


class FileCreate(FileBase):
    user_id: int


# CUSTOMER -------------------------------------------------------------
class CustomerBase(BaseModel):
    name: str


class CustomerCreate(CustomerBase):
    user_id: int


class CustomerLite(CustomerBase):
    id: int
    num_invoices: int

    class Config:
        orm_mode = True


# INVOICE -------------------------------------------------------------
class InvoiceBase(BaseModel):
    number_id: int
    reason: str
    tax_1: Optional[float]
    tax_2: Optional[float]
    with_taxes: Optional[bool]
    created: datetime
    updated: datetime
    customer_id: int


class InvoiceCreate(InvoiceBase):
    user_id: int


class InvoiceLite(InvoiceBase):
    id: int

    class Config:
        orm_mode = True


# FILE -------------------------------------------------------------
class File(FileBase):
    id: int
    bill_to: BillTo
    services: list[Service] = []

    class Config:
        orm_mode = True


# INVOICE -------------------------------------------------------------
class Invoice(InvoiceBase):
    id: int
    files: List[File] = []

    class Config:
        orm_mode = True


# CUSTOMER -------------------------------------------------------------
class Customer(CustomerBase):
    id: int
    num_invoices: int
    invoices: List[Invoice] = []

    class Config:
        orm_mode = True
