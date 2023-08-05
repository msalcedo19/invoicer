import logging
from typing import Optional, Union, List
from pydantic import BaseModel

from fastapi import APIRouter, Depends, Form, UploadFile, status, HTTPException
from sqlalchemy.orm import Session

from ms_invoicer.db_pool import get_db
from ms_invoicer.file_helpers import process_file, process_pdf
from ms_invoicer.security_helper import get_current_user
from ms_invoicer.sql_app import crud, schemas

router = APIRouter()
log = logging.getLogger(__name__)


class Generate_PDF(BaseModel):
    bill_to_id: str
    invoice: Optional[schemas.InvoiceBase]
    contracts: List[schemas.ServiceCreateNoFile]
    use_existing_invoice: bool = False
    with_taxes: bool = True


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
    with_taxes: bool = Form(),
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_created = await process_file(
        file=file,
        invoice_id=int(invoice_id),
        bill_to_id=int(bill_to_id),
        current_user_id=current_user.id,
        with_taxes=with_taxes,
    )
    return crud.get_file(
        db=db, model_id=file_created.id, current_user_id=current_user.id
    )


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
    body: Generate_PDF,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = None
    new_invoice = None
    if body.invoice:
        result = crud.get_invoices_by_number_id(
            db=db,
            number_id=body.invoice.number_id,
            customer_id=body.invoice.customer_id,
            current_user_id=current_user.id,
        )

    if not result or body.use_existing_invoice: # TODO: remover atributo innecesario o hacer mensaje en UI cuando se este usando
        try:
            if result:
                new_invoice = result
            else:
                obj_dict = body.invoice.dict()
                obj_dict["user_id"] = current_user.id
                new_invoice = crud.create_invoice(
                    db=db, model=schemas.InvoiceCreate(**obj_dict)
                )
            return await process_pdf(
                db=db,
                invoice=new_invoice,
                bill_to_id=body.bill_to_id,
                contracts=body.contracts,
                current_user=current_user,
                with_taxes=body.with_taxes,
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
