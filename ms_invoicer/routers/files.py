from fastapi import Depends, FastAPI, UploadFile, APIRouter, Form
from sqlalchemy.orm import Session
from ms_invoicer.sql_app import crud, schemas, models
from ms_invoicer.file_helpers import process_file, save_file
from ms_invoicer.db_pool import get_db
from typing import Union

router = APIRouter()


@router.get("/files/{invoice_id}", response_model=list[schemas.File])
def get_files_by_invoice(invoice_id: int, db: Session = Depends(get_db)):
    return crud.get_files_by_invoice(db=db, model_id=invoice_id)


@router.get("/files/", response_model=list[schemas.File])
def get_files(db: Session = Depends(get_db)):
    return crud.get_files(db=db)


@router.patch("/files/{model_id}", response_model=Union[schemas.File, None])
def patch_customer(model_update: dict, model_id: int, db: Session = Depends(get_db)):
    result = crud.patch_file(db=db, model_id=model_id, update_dict=model_update)
    if result:
        return crud.get_file(db=db, model_id=model_id)
    else:
        return None

@router.post("/upload_file/", response_model=schemas.File)
async def create_upload_file(
    invoice_id: str = Form(), file: UploadFile = Form(), db: Session = Depends(get_db)
):
    file_path = "temp/" + file.filename
    save_file(file_path, file)

    file_created = await process_file(file_path, int(invoice_id))
    return crud.get_file(db=db, model_id=file_created.id)
