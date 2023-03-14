import logging
from typing import List
from ms_invoicer.config import LOG_LEVEL
from fastapi import Depends, FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from ms_invoicer.sql_app import crud, schemas, models
from ms_invoicer.event_handler import register_event_handlers
from ms_invoicer.db_pool import get_db
from ms_invoicer.invoice_helper import build_pdf
from ms_invoicer.file_helpers import upload_file, process_file, save_file
from ms_invoicer.routers import customer, invoice, files

api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
api.include_router(customer.router, tags=["Customer"])
api.include_router(invoice.router, tags=["Invoice"])
api.include_router(files.router, tags=["Files"])

logging.basicConfig(format="[%(asctime)s] %(levelname)-8s - %(message)s", level=LOG_LEVEL)
log = logging.getLogger(__name__)

register_event_handlers()


@api.get("/test")
async def test(db: Session = Depends(get_db), file: UploadFile = Form()):
    #build_pdf(html_name="template01.html", pdf_name="invoice01.pdf", invoice=crud.get_invoice(db=db, model_id=6))
    file_path = "temp/" + file.filename

    save_file(file_path, file)

    file_created = await process_file(file_path, 1)
    return {"status": "OK"}

@api.get("/")
def api_status():
    """Returns a detailed status of the service including all dependencies"""
    # TODO: Should replace this with database connection / service checks
    return {"status": "OK"}


@api.get("/global/{global_name}", response_model=schemas.Global)
def get_global(global_name: str, db: Session = Depends(get_db)):
    return crud.get_global(db=db, global_name=global_name)


@api.get("/service/", response_model=List[schemas.Service])
def get_services(db: Session = Depends(get_db)):
    return crud.get_services(db=db)


@api.post("/bill_to/", response_model=schemas.BillTo)
def create_bill_to(model: schemas.BillToCreate, db: Session = Depends(get_db)):
    return crud.create_billto(db=db, model=model)
