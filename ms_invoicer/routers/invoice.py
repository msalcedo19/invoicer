from typing import List, Union
import logging
from ms_invoicer.config import LOG_LEVEL
from fastapi import Depends, APIRouter, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from ms_invoicer.sql_app import crud, schemas, models
from ms_invoicer.db_pool import get_db

router = APIRouter()


@router.post("/invoice/", response_model=schemas.InvoiceLite)
def post_invoice(invoice: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    return crud.create_invoice(db=db, model=invoice)


@router.patch("/invoice/{model_id}", response_model=Union[schemas.Invoice, None])
def patch_invoice(model_update: dict, model_id: int, db: Session = Depends(get_db)):
    result = crud.patch_invoice(db=db, model_id=model_id, update_dict=model_update)
    if result:
        return crud.get_invoice(db=db, model_id=model_id)
    else:
        return None


@router.get("/invoice/{invoice_id}", response_model=Union[schemas.Invoice, None])
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    return crud.get_invoice(db=db, model_id=invoice_id)


@router.get("/invoice/", response_model=List[schemas.Invoice])
def get_invoice(db: Session = Depends(get_db)):
    return crud.get_invoices(db=db)


@router.delete("/invoice/{model_id}", status_code=status.HTTP_200_OK)
def delete_invoice(model_id: int, db: Session = Depends(get_db)):
    files = crud.get_files_by_invoice(db=db, model_id=model_id)
    for file in files:
        crud.delete_services_by_file(db=db, model_id=file.id)
    crud.delete_files_by_invoice(db=db, model_id=model_id)
    return crud.delete_invoice(db=db, model_id=model_id)
