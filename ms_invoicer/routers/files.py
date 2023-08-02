from typing import Union

from fastapi import APIRouter, Depends, Form, UploadFile, status
from sqlalchemy.orm import Session

from ms_invoicer.db_pool import get_db
from ms_invoicer.file_helpers import process_file
from ms_invoicer.security_helper import get_current_user
from ms_invoicer.sql_app import crud, schemas

router = APIRouter()


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
        with_taxes=with_taxes
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
