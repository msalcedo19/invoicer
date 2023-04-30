from typing import Union

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ms_invoicer.db_pool import get_db
from ms_invoicer.security_helper import get_current_user
from ms_invoicer.sql_app import crud, schemas

router = APIRouter()


@router.get("/customer", response_model=list[schemas.Customer])
async def get_customers(
    current_user: schemas.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud.get_customers(
        db=db, current_user_id=current_user.id, skip=skip, limit=limit
    )


@router.get("/customer/{model_id}", response_model=Union[schemas.Customer, None])
def get_customer(
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_customer(db=db, model_id=model_id, current_user_id=current_user.id)


@router.patch("/customer/{model_id}", response_model=Union[schemas.Customer, None])
def patch_customer(
    model_update: dict,
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = crud.patch_customer(
        db=db,
        model_id=model_id,
        current_user_id=current_user.id,
        update_dict=model_update,
    )
    if result:
        return crud.get_customer(
            db=db, model_id=model_id, current_user_id=current_user.id
        )
    else:
        return None


@router.delete("/customer/{customer_id}", status_code=status.HTTP_200_OK)
def delete_customer(
    customer_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoices = crud.get_invoices_by_customer(
        db=db, model_id=customer_id, current_user_id=current_user.id
    )
    for invoice in invoices:
        files = crud.get_files_by_invoice(
            db=db, model_id=invoice.id, current_user_id=current_user.id
        )
        for file in files:
            crud.delete_services_by_file(
                db=db, model_id=file.id, current_user_id=current_user.id
            )
        crud.delete_files_by_invoice(
            db=db, model_id=invoice.id, current_user_id=current_user.id
        )
    crud.delete_invoices_by_customer(
        db=db, model_id=customer_id, current_user_id=current_user.id
    )
    return crud.delete_customer(
        db=db, model_id=customer_id, current_user_id=current_user.id
    )


@router.post("/customer", response_model=schemas.CustomerLite)
def post_customer(
    customer: schemas.CustomerBase,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    obj_dict = customer.dict()
    obj_dict["user_id"] = current_user.id
    return crud.create_customer(db=db, model=schemas.CustomerCreate(**obj_dict))
