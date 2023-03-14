from typing import Union
import logging
from ms_invoicer.config import LOG_LEVEL
from fastapi import Depends, APIRouter, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from ms_invoicer.sql_app import crud, schemas, models
from ms_invoicer.db_pool import get_db

router = APIRouter()


@router.post("/invoice/", response_model=schemas.Invoice)
def post_invoice(invoice: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    return crud.create_invoice(db=db, model=invoice)


@router.get("/invoice/", response_model=list[schemas.Invoice])
def get_invoices(db: Session = Depends(get_db)):
    return crud.get_invoices(db=db)


@router.get("/invoice/{customer_id}", response_model=list[schemas.Invoice])
def get_invoice_by_customer(customer_id: int, db: Session = Depends(get_db)):
    return crud.get_invoice_by_customer(db=db, model_id=customer_id)


@router.delete("/invoice/{model_id}", status_code=status.HTTP_200_OK)
def delete_invoice(model_id: int, db: Session = Depends(get_db)):
    files = crud.get_files_by_invoice(db=db, model_id=model_id)
    for file in files:
        crud.delete_service_by_file(db=db, model_id=file.id)
    crud.delete_file_by_invoice(db=db, model_id=model_id)
    return crud.delete_invoice(db=db, model_id=model_id)
