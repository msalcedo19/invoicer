from datetime import datetime
from typing import List, Union, Optional

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


# Template -------------------------------------------------------------
class TemplateBase(BaseModel):
    name: str
    created: datetime
    updated: datetime


class TemplateCreate(TemplateBase):
    user_id: int


class Template(TemplateBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


# SERVICE -------------------------------------------------------------
class ServiceBase(BaseModel):
    title: str
    amount: float
    currency: str
    hours: float
    price_unit: float
    file_id: int
    invoice_id: int


class ServiceCreate(ServiceBase):
    user_id: int

class ServiceCreateNoFile(BaseModel):
    title: str
    amount: float
    currency: str
    hours: float
    price_unit: float

class Service(ServiceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# BILLTO -------------------------------------------------------------
class BillToBase(BaseModel):
    to: str
    addr: str
    phone: str
    email: str


class BillToCreate(BillToBase):
    user_id: int


class BillToUpdate(BaseModel):
    to: Optional[str] = None
    addr: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class BillTo(BillToBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


# FILE -------------------------------------------------------------
class FileBase(BaseModel):
    s3_xlsx_url: Union[str, None]
    s3_pdf_url: Union[str, None]
    pages_xlsx: Union[str, None]
    created: datetime
    invoice_id: int
    bill_to_id: int


class FileCreate(FileBase):
    user_id: int


class FileUpdate(BaseModel):
    s3_xlsx_url: Optional[str] = None
    s3_pdf_url: Optional[str] = None
    pages_xlsx: Optional[str] = None
    created: Optional[datetime] = None
    invoice_id: Optional[int] = None
    bill_to_id: Optional[int] = None


# CUSTOMER -------------------------------------------------------------
class CustomerBase(BaseModel):
    name: str


class CustomerCreate(CustomerBase):
    user_id: int


class CustomerUpdate(BaseModel):
    name: Optional[str] = None


# INVOICE -------------------------------------------------------------
class InvoiceBase(BaseModel):
    number_id: int
    reason: str
    tax_1: Optional[float]
    tax_2: Optional[float]
    with_taxes: Optional[bool]
    with_tables: Optional[bool]
    created: datetime
    updated: datetime
    customer_id: int


class InvoiceCreate(InvoiceBase):
    user_id: int


class InvoiceUpdate(BaseModel):
    number_id: Optional[int] = None
    reason: Optional[str] = None
    tax_1: Optional[float] = None
    tax_2: Optional[float] = None
    with_taxes: Optional[bool] = None
    with_tables: Optional[bool] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    customer_id: Optional[int] = None


class InvoiceLite(InvoiceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# FILE -------------------------------------------------------------
class File(FileBase):
    id: int
    bill_to: BillTo
    services: list[Service] = []

    model_config = ConfigDict(from_attributes=True)


class FileLite(FileBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# INVOICE -------------------------------------------------------------
class Invoice(InvoiceBase):
    id: int
    files: List[File] = []

    model_config = ConfigDict(from_attributes=True)


# CUSTOMER -------------------------------------------------------------
class Customer(CustomerBase):
    id: int
    num_invoices: int

    model_config = ConfigDict(from_attributes=True)


class CustomerFull(CustomerBase):
    id: int
    invoices: List[Invoice]

    model_config = ConfigDict(from_attributes=True)

# TOTALS
class TotalAndCustomer(BaseModel):
    total: int
    customers: List[Customer]


class TotalAndInvoices(BaseModel):
    total: int
    invoices: List[Invoice]
