from typing import List, Union, Dict

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from ms_invoicer.config import S3_BUCKET_NAME

from ms_invoicer.db_pool import get_db
from ms_invoicer.security_helper import get_current_user
from ms_invoicer.sql_app import crud, schemas
from ms_invoicer.utils import delete_file_from_s3

router = APIRouter()


@router.get("/customer", response_model=schemas.TotalAndCustomer)
async def get_customers(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start = 0
    return schemas.TotalAndCustomer(
        total=crud.get_total_customers(db=db, current_user_id=current_user.id),
        customers=crud.get_customers(
            db=db, current_user_id=current_user.id, skip=start
        ),
    )


@router.get("/customer/{model_id}", response_model=Union[schemas.CustomerFull, None])
def get_customer(
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_customer(db=db, model_id=model_id, current_user_id=current_user.id)


@router.get("/customer/{model_id}/invoices", response_model=schemas.TotalAndInvoices)
def get_customer_invoices(
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start = 0
    return schemas.TotalAndInvoices(
        total=crud.get_total_invoices_by_customer(
            db=db, model_id=model_id, current_user_id=current_user.id
        ),
        invoices=crud.get_invoices_by_customer(
            db=db,
            model_id=model_id,
            current_user_id=current_user.id,
            skip=start,
        ),
    )


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
        files_to_delete = []
        for file in files:
            crud.delete_services_by_file(
                db=db, model_id=file.id, current_user_id=current_user.id
            )
            if file.s3_pdf_url:
                file_name = file.s3_pdf_url.split("/")[3]
                files_to_delete.append(file_name)
            if file.s3_xlsx_url:
                file_name = file.s3_pdf_url.split("/")[3]
                files_to_delete.append(file_name)
        crud.delete_files_by_invoice(
            db=db, model_id=invoice.id, current_user_id=current_user.id
        )
    crud.delete_invoices_by_customer(
        db=db, model_id=customer_id, current_user_id=current_user.id
    )
    delete_file_from_s3(file_names=files_to_delete, bucket_name=S3_BUCKET_NAME)
    return crud.delete_customer(
        db=db, model_id=customer_id, current_user_id=current_user.id
    )


@router.post("/customer", response_model=schemas.Customer)
def post_customer(
    customer: schemas.CustomerBase,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    obj_dict = customer.dict()
    obj_dict["user_id"] = current_user.id
    return crud.create_customer(db=db, model=schemas.CustomerCreate(**obj_dict))


@router.get("/get_all_customer", response_model=list[schemas.Customer])
async def get_all_customers(
    current_user: schemas.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud.get_all_customers(db=db, skip=skip, limit=limit)


@router.patch("/update_customer_data")
def patch_invoice(
    customer_id: int,
    new_user_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    model_update = {"user_id": new_user_id}

    result = crud.patch_all_customer_by_user_id(
        db=db,
        user_id=current_user.id,
        update_dict=model_update,
    )
    result = crud.patch_all_invoice_by_customer_user_id(
        db=db,
        customer_id=customer_id,
        user_id=current_user.id,
        update_dict=model_update,
    )
    return {"rows affected": result}
