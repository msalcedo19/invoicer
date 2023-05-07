from typing import List, Union

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from ms_invoicer.db_pool import get_db
from ms_invoicer.security_helper import get_current_user
from ms_invoicer.sql_app import crud, schemas

router = APIRouter()


@router.post("/invoice", response_model=schemas.InvoiceLite)
def post_invoice(
    invoice: schemas.InvoiceBase,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = crud.get_invoices_by_number_id(
        db=db, number_id=invoice.number_id, current_user_id=current_user.id
    )
    if not result:
        obj_dict = invoice.dict()
        obj_dict["user_id"] = current_user.id
        return crud.create_invoice(db=db, model=schemas.InvoiceCreate(**obj_dict))
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Existe una factura con ese numéro de factura",
    )


@router.patch("/invoice/{model_id}", response_model=Union[schemas.Invoice, None])
def patch_invoice(
    model_update: dict,
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = crud.patch_invoice(
        db=db,
        model_id=model_id,
        update_dict=model_update,
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
):
    return crud.get_invoice(db=db, model_id=invoice_id, current_user_id=current_user.id)


@router.get("/invoice", response_model=List[schemas.Invoice])
def get_invoice(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_invoices(db=db, current_user_id=current_user.id)


@router.delete("/invoice/{model_id}", status_code=status.HTTP_200_OK)
def delete_invoice(
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    files = crud.get_files_by_invoice(
        db=db, model_id=model_id, current_user_id=current_user.id
    )
    for file in files:
        crud.delete_services_by_file(
            db=db, model_id=file.id, current_user_id=current_user.id
        )
    crud.delete_files_by_invoice(
        db=db, model_id=model_id, current_user_id=current_user.id
    )
    return crud.delete_invoice(
        db=db, model_id=model_id, current_user_id=current_user.id
    )
