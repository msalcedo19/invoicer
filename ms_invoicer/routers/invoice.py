from typing import List, Optional, Union

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ms_invoicer.config import S3_BUCKET_NAME

from ms_invoicer.db_pool import get_db
from ms_invoicer.security_helper import get_current_user
from ms_invoicer.sql_app import crud, schemas
from ms_invoicer.utils import delete_file_from_s3

router = APIRouter()


@router.post("/invoice", response_model=schemas.InvoiceLite)
def post_invoice(
    invoice: schemas.InvoiceBase,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.InvoiceLite:
    result = crud.get_invoices_by_number_id(
        db=db,
        number_id=invoice.number_id,
        customer_id=invoice.customer_id,
        current_user_id=current_user.id,
    )
    if not result:
        obj_dict = invoice.model_dump()
        obj_dict["user_id"] = current_user.id
        return crud.create_invoice(db=db, model=schemas.InvoiceCreate(**obj_dict))
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Existe una factura con ese numéro de factura",
    )


@router.patch("/invoice/{model_id}", response_model=Union[schemas.Invoice, None])
def patch_invoice(
    model_update: schemas.InvoiceUpdate,
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Optional[schemas.Invoice]:
    update_dict = model_update.model_dump(exclude_unset=True)
    if "number_id" in update_dict and not isinstance(
        update_dict.get("number_id", None), int
    ):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="El número de factura debe ser un número",
        )
    result = crud.patch_invoice(
        db=db,
        model_id=model_id,
        update_dict=update_dict,
        current_user_id=current_user.id,
    )
    if result:
        return crud.get_invoice(
            db=db, model_id=model_id, current_user_id=current_user.id
        )
    else:
        return None


@router.get("/invoice/{invoice_id}", response_model=Union[schemas.Invoice, None])
def get_invoice(
    invoice_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Optional[schemas.Invoice]:
    return crud.get_invoice(db=db, model_id=invoice_id, current_user_id=current_user.id)


@router.get("/invoice", response_model=List[schemas.Invoice])
def get_invoice(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[schemas.Invoice]:
    return crud.get_invoices(db=db, current_user_id=current_user.id)


@router.delete("/invoice/{model_id}", status_code=status.HTTP_200_OK)
def delete_invoice(
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> int:
    files = crud.get_files_by_invoice(
        db=db, model_id=model_id, current_user_id=current_user.id
    )
    files_to_delete = []
    for file in files:
        crud.delete_services_by_file(
            db=db, model_id=file.id, current_user_id=current_user.id
        )
        if file.s3_pdf_url:
            file_name = file.s3_pdf_url.split("/")[3]
            files_to_delete.append(file_name)
        if file.s3_xlsx_url:
            file_name = file.s3_xlsx_url.split("/")[3]
            files_to_delete.append(file_name)
    crud.delete_files_by_invoice(
        db=db, model_id=model_id, current_user_id=current_user.id
    )
    delete_file_from_s3(file_names=files_to_delete, bucket_name=S3_BUCKET_NAME)
    return crud.delete_invoice(
        db=db, model_id=model_id, current_user_id=current_user.id
    )
