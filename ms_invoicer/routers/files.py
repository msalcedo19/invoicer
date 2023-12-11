from datetime import datetime
import logging
import json
from typing import Dict, Optional, Union, List
from pydantic import BaseModel

from fastapi import APIRouter, Depends, Form, UploadFile, status, HTTPException, Body
from sqlalchemy.orm import Session

from ms_invoicer.db_pool import get_db
from ms_invoicer.file_helpers import (
    extract_pages,
    generate_summary_by_date,
    process_file,
    process_pdf,
)
from ms_invoicer.security_helper import get_current_user
from ms_invoicer.sql_app import crud, schemas
from ms_invoicer.utils import get_current_date

router = APIRouter()
log = logging.getLogger(__name__)


class Generate_PDF(BaseModel):
    bill_to_id: str = (Form(),)
    invoice: Optional[schemas.InvoiceBase] = (Form(),)
    contracts: List[schemas.ServiceCreateNoFile] = (Form(),)
    file: Optional[UploadFile] = Form()


@router.get("/files/{file_id}", response_model=schemas.File)
def get_file(
    file_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_file(db=db, model_id=file_id, current_user_id=current_user.id)


@router.get("/files", response_model=list[schemas.File])
def get_files(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_files(db=db, current_user_id=current_user.id)


@router.patch("/files/{model_id}", response_model=Union[schemas.File, None])
def patch_file(
    model_update: dict,
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = crud.patch_file(
        db=db,
        model_id=model_id,
        update_dict=model_update,
        current_user_id=current_user.id,
    )
    if result:
        return crud.get_file(db=db, model_id=model_id, current_user_id=current_user.id)
    else:
        return None


@router.delete("/files/{model_id}", status_code=status.HTTP_200_OK)
def delete_file(
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file = crud.get_file(db=db, model_id=model_id, current_user_id=current_user.id)
    crud.delete_services_by_file(
        db=db, model_id=file.id, current_user_id=current_user.id
    )
    return crud.delete_file(db=db, model_id=model_id, current_user_id=current_user.id)


class SummaryRequest(BaseModel):
    customer_id: str
    start_date: str
    end_date: str


@router.post("/summary")
async def generate_summary(
    summary_request: SummaryRequest = Body(...),
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Define the format of your date string
    date_format = "%Y-%m-%d"

    # Parse the string into a datetime object
    start_parsed_date = datetime.strptime(summary_request.start_date, date_format)
    start_parsed_date = start_parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_parsed_date = datetime.strptime(summary_request.end_date, date_format)
    end_parsed_date = end_parsed_date.replace(hour=23, minute=59, second=59, microsecond=99)
    file_path = await generate_summary_by_date(
        db=db,
        customer_id=summary_request.customer_id,
        current_user=current_user,
        start_date=start_parsed_date,
        end_date=end_parsed_date,
    )
    return {"s3_file_path": file_path}


@router.post("/get_pages", response_model=Dict[str, List[str]])
async def get_pages(
    file: UploadFile = Form(),
    current_user: schemas.User = Depends(get_current_user)
):
    response = extract_pages(uploaded_file=file, current_user_id=current_user.id)
    return {"pages": response}


@router.post("/file", response_model=schemas.File)
async def create_file(
    file: schemas.FileCreate,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    obj_dict = file.dict()
    obj_dict["user_id"] = current_user.id
    return crud.create_file(
        db=db, model=schemas.FileCreate(**obj_dict), current_user_id=current_user.id
    )


@router.post("/generate_pdf")
async def generate_pdf(
    file: Optional[UploadFile] = Form(None),
    invoice_number_id: str = Form(None),
    invoice_customer_id: str = Form(None),
    bill_to_id: str = Form(),
    with_taxes: bool = Form(None),
    with_tables: bool = Form(None),
    invoice: Optional[str] = Form(None),
    contracts: str = Form(),
    pages: str = Form(),
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = None
    new_invoice = None

    try:
        if invoice:
            invoice_json = json.loads(invoice)
            invoice_json["created"] = get_current_date()
            invoice_json["updated"] = get_current_date()
            invoice_schema = schemas.InvoiceBase(**invoice_json)
            if with_taxes is not None:
                invoice_schema.with_taxes = with_taxes
            if with_tables is not None:
                invoice_schema.with_tables = with_tables
            invoice: schemas.InvoiceBase = invoice_schema
        contracts: List[schemas.ServiceCreateNoFile] = [
            schemas.ServiceCreateNoFile(**contract)
            for contract in json.loads(contracts)
        ]

        pages_json: List[str] = json.loads(pages)
        pages_formatted: List[str] = []
        for page in pages_json:
            if "," in page:
                pages_formatted.append(page.replace(",", "-"))
            else:
                pages_formatted.append(page)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON Invalido")

    if invoice:
        result = crud.get_invoices_by_number_id(
            db=db,
            number_id=invoice.number_id,
            customer_id=invoice.customer_id,
            current_user_id=current_user.id,
        )

    if not result:
        invoice_created = False
        try:
            if (
                not invoice
                and invoice_customer_id is not None
                and invoice_number_id is not None
            ):
                new_invoice = crud.get_invoices_by_number_id(
                    db=db,
                    number_id=invoice_number_id,
                    customer_id=invoice_customer_id,
                    current_user_id=current_user.id,
                )
                if with_taxes is not None and with_tables is not None:
                    crud.patch_invoice(
                        db=db,
                        model_id=new_invoice.id,
                        current_user_id=current_user.id,
                        update_dict={"with_taxes": with_taxes, "with_tables": with_tables},
                    )
                    new_invoice.with_taxes = with_taxes
                    new_invoice.with_tables = with_tables
            else:
                obj_dict = invoice.dict()
                obj_dict["user_id"] = current_user.id
                new_invoice = crud.create_invoice(
                    db=db, model=schemas.InvoiceCreate(**obj_dict)
                )
                invoice_created = True

            file_created, xlsx_local_path = await process_file(
                file=file,
                invoice_id=int(new_invoice.id),
                bill_to_id=int(bill_to_id),
                current_user_id=current_user.id,
                pages=pages_formatted,
            )

            return await process_pdf(
                db=db,
                invoice=new_invoice,
                bill_to_id=bill_to_id,
                contracts=contracts,
                current_user=current_user,
                new_file_obj=file_created,
                xlsx_local_path=xlsx_local_path,
                pages=pages_formatted,
            )
        except Exception as e:
            log.error("Customer {} - {}".format(current_user.id, e))
            files = crud.get_files_by_invoice(
                db=db, model_id=new_invoice.id, current_user_id=current_user.id
            )
            files = sorted(files, key=lambda x: x.created, reverse=True)
            if len(files) > 0:
                crud.delete_services_by_file(
                    db=db, model_id=files[0].id, current_user_id=current_user.id
                )
                crud.delete_file(db=db, model_id=files[0].id, current_user_id=current_user.id)

            if invoice_created:
                crud.delete_invoice(
                    db=db, model_id=new_invoice.id, current_user_id=current_user.id
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Error al generar la factura",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Existe una factura con ese numéro de factura",
        )
