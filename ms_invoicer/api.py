from typing import Union
import logging
from ms_invoicer.config import LOG_LEVEL
from fastapi import Depends, FastAPI, UploadFile, status
from sqlalchemy.orm import Session
from ms_invoicer.sql_app import crud, schemas, models
from ms_invoicer.file_helpers import process_file, save_file
from ms_invoicer.event_handler import register_event_handlers
from ms_invoicer.db_pool import get_db

api = FastAPI()
logging.basicConfig(format="[%(asctime)s] %(levelname)-8s - %(message)s", level=LOG_LEVEL)
log = logging.getLogger(__name__)

register_event_handlers()


@api.get("/")
def api_status():
    """Returns a detailed status of the service including all dependencies"""
    # TODO: Should replace this with database connection / service checks
    return {"status": "OK"}


@api.get("/customer/", response_model=list[schemas.Customer])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_customers(db=db, skip=skip, limit=limit)


@api.get("/customer/{model_id}", response_model=Union[schemas.Customer, None])
def get_customer(model_id: int, db: Session = Depends(get_db)):
    return crud.get_customer(db=db, model_id=model_id)


@api.patch("/customer/{model_id}", response_model=Union[schemas.Customer, None])
def patch_customer(model_update: dict, model_id: int, db: Session = Depends(get_db)):
    result = crud.patch_customer(db=db, model_id=model_id, update_dict=model_update)
    if result:
        return crud.get_customer(db=db, model_id=model_id)
    else:
        return None


@api.delete("/customer/{model_id}", status_code=status.HTTP_200_OK)
def delete_customer(model_id: int, db: Session = Depends(get_db)):
    return crud.delete_customer(db=db, model_id=model_id)


@api.post("/customer/", response_model=schemas.Customer)
def post_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db=db, model=customer)


@api.post("/file/")
async def create_upload_file(file: UploadFile, db: Session = Depends(get_db)):
    file_path = 'temp/' + file.filename
    output_path = 'temp/new {}'.format(file.filename)

    save_file(file_path, file)
    file.file.seek(0)
    save_file(output_path, file)

    file_created = await process_file(file_path, output_path)
    return crud.create_file(db=db, model=file_created)


@api.post("/bill_to/", response_model=schemas.BillTo)
def create_bill_to(model: schemas.BillToCreate, db: Session = Depends(get_db)):
    return crud.create_billto(db=db, model=model)

