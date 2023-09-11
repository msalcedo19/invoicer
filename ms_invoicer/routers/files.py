import logging
import json
from typing import Dict, Optional, Union, List
from pydantic import BaseModel

from fastapi import APIRouter, Depends, Form, UploadFile, status, HTTPException
from sqlalchemy.orm import Session

from ms_invoicer.db_pool import get_db
from ms_invoicer.file_helpers import extract_pages, process_file, process_pdf
from ms_invoicer.security_helper import get_current_user
from ms_invoicer.sql_app import crud, schemas

router = APIRouter()
log = logging.getLogger(__name__)


class Generate_PDF(BaseModel):
    bill_to_id: str = Form(),
    invoice: Optional[schemas.InvoiceBase] = Form(),
    contracts: List[schemas.ServiceCreateNoFile] = Form(),
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


@router.post("/upload_file", response_model=schemas.File)
async def create_upload_file(
    invoice_id: str = Form(),
    bill_to_id: str = Form(),
    file: UploadFile = Form(),
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_created = await process_file(
        file=file,
        invoice_id=int(invoice_id),
        bill_to_id=int(bill_to_id),
        current_user_id=current_user.id,
    )
    return crud.get_file(
        db=db, model_id=file_created.id, current_user_id=current_user.id
    )

@router.post("/get_pages", response_model=Dict[str, List[str]])
async def get_pages(
    file: UploadFile = Form(),
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    response = extract_pages(file=file, current_user_id=current_user.id)
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
            invoice_schema = schemas.InvoiceBase(**json.loads(invoice))
            if with_taxes is not None:
                invoice_schema.with_taxes = with_taxes
            invoice: schemas.InvoiceBase = invoice_schema
        contracts: List[schemas.ServiceCreateNoFile] = [schemas.ServiceCreateNoFile(**contract) for contract in json.loads(contracts)]
        pages: List[str] = [page for page in json.loads(pages)]
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data provided")

    if invoice:
        result = crud.get_invoices_by_number_id(
            db=db,
            number_id=invoice.number_id,
            customer_id=invoice.customer_id,
            current_user_id=current_user.id,
        )

    if not result:
        try:
            if result:
                new_invoice = result
            elif not invoice and invoice_customer_id is not None and invoice_number_id is not None:
                new_invoice = crud.get_invoices_by_number_id(
                    db=db,
                    number_id=invoice_number_id,
                    customer_id=invoice_customer_id,
                    current_user_id=current_user.id,
                )
                if with_taxes is not None:
                    crud.patch_invoice(db=db, model_id=new_invoice.id, current_user_id=current_user.id, update_dict={"with_taxes": with_taxes}) #TODO: Manejar evento cuando falla la actualización
                    new_invoice.with_taxes = with_taxes
            else:
                obj_dict = invoice.dict()
                obj_dict["user_id"] = current_user.id
                new_invoice = crud.create_invoice(
                    db=db, model=schemas.InvoiceCreate(**obj_dict)
                )

            file_created, xlsx_local_path = await process_file(
                file=file,
                invoice_id=int(new_invoice.id),
                bill_to_id=int(bill_to_id),
                current_user_id=current_user.id,
                pages=pages,
            )

            return await process_pdf(
                db=db,
                invoice=new_invoice,
                bill_to_id=bill_to_id,
                contracts=contracts,
                current_user=current_user,
                new_file_obj=file_created,
                xlsx_local_path=xlsx_local_path
            )
        except Exception as e:
            log.error("Customer {} - {}".format(current_user.id, e))
            if new_invoice:
                files = crud.get_files_by_invoice(
                    db=db, model_id=new_invoice.id, current_user_id=current_user.id
                )
                for file in files:
                    crud.delete_services_by_file(
                        db=db, model_id=file.id, current_user_id=current_user.id
                    )
                crud.delete_files_by_invoice(
                    db=db, model_id=new_invoice.id, current_user_id=current_user.id
                )
                crud.delete_invoice(
                    db=db, model_id=new_invoice.id, current_user_id=current_user.id
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Existe una factura con ese numéro de factura",
        )
