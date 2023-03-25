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
    price_unit: int
    file_id: int


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
    contract_id: int


class BillToCreate(BillToBase):
    pass


class BillTo(BillToBase):
    id: int

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

    class Config:
        orm_mode = True


class FileBase(BaseModel):
    s3_xlsx_url: str
    s3_pdf_url: Union[str, None]
    created: datetime
    invoice_id: int


class FileCreate(FileBase):
    pass


class ContractBase(BaseModel):
    name: str
    price_unit: int
    customer_id: int


class ContractCreate(ContractBase):
    pass


class ContractLite(ContractBase):
    id: int

    class Config:
        orm_mode = True


class CustomerBase(BaseModel):
    name: str


class CustomerCreate(CustomerBase):
    pass


class CustomerLite(CustomerBase):
    id: int
    num_contracts: int

    class Config:
        orm_mode = True


class Customer(CustomerBase):
    id: int
    contracts: List[ContractLite] = []

    class Config:
        orm_mode = True


class InvoiceBase(BaseModel):
    number_id: int
    reason: str
    tax_1: int
    tax_2: int
    created: datetime
    updated: datetime
    contract_id: int
    bill_to_id: int


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceLite(InvoiceBase):
    id: int

    class Config:
        orm_mode = True

class File(FileBase):
    id: int
    services: list[Service] = []

    class Config:
        orm_mode = True

class Invoice(InvoiceBase):
    id: int
    bill_to: BillTo
    files: List[File] = []

    class Config:
        orm_mode = True


class Contract(ContractBase):
    id: int
    invoices: List[Invoice] = []

    class Config:
        orm_mode = True