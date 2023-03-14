from typing import Union
import logging
from ms_invoicer.config import LOG_LEVEL
from fastapi import Depends, status, Form, APIRouter
from sqlalchemy.orm import Session
from ms_invoicer.sql_app import crud, schemas, models
from ms_invoicer.db_pool import get_db

router = APIRouter()


@router.get("/customer/", response_model=list[schemas.Customer])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_customers(db=db, skip=skip, limit=limit)


@router.get("/customer/{model_id}", response_model=Union[schemas.Customer, None])
def get_customer(model_id: int, db: Session = Depends(get_db)):
    return crud.get_customer(db=db, model_id=model_id)


@router.patch("/customer/{model_id}", response_model=Union[schemas.Customer, None])
def patch_customer(model_update: dict, model_id: int, db: Session = Depends(get_db)):
    result = crud.patch_customer(db=db, model_id=model_id, update_dict=model_update)
    if result:
        return crud.get_customer(db=db, model_id=model_id)
    else:
        return None


@router.delete("/customer/{model_id}", status_code=status.HTTP_200_OK)
def delete_customer(model_id: int, db: Session = Depends(get_db)):
    invoices = crud.get_invoice_by_customer(db=db, model_id=model_id)
    for invoice in invoices:
        files = crud.get_files_by_invoice(db=db, model_id=invoice.id)
        for file in files:
            crud.delete_service_by_file(db=db, model_id=file.id)
        crud.delete_file_by_invoice(db=db, model_id=invoice.id)
    crud.delete_invoices_by_customer(db=db, model_id=model_id)
    return crud.delete_customer(db=db, model_id=model_id)


@router.post("/customer/", response_model=schemas.Customer)
def post_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db=db, model=customer)
