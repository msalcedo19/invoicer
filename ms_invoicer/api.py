from datetime import datetime
import logging
from typing import List

from ms_invoicer.config import LOG_LEVEL
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from ms_invoicer.sql_app import crud, schemas
from ms_invoicer.event_handler import register_event_handlers
from ms_invoicer.db_pool import get_db
from ms_invoicer.utils import create_folders
from ms_invoicer.routers import customer, invoice, files, contract

create_folders()
api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
api.include_router(customer.router, tags=["Customer"])
api.include_router(contract.router, tags=["Contract"])
api.include_router(invoice.router, tags=["Invoice"])
api.include_router(files.router, tags=["Files"])

logging.basicConfig(
    format="[%(asctime)s] %(levelname)-8s - %(message)s", level=LOG_LEVEL
)
log = logging.getLogger(__name__)

register_event_handlers()


@api.get("/")
def api_status():
    """Returns a detailed status of the service including all dependencies"""
    # TODO: Should replace this with database connection / service checks
    return {"status": "OK"}


@api.post("/breadcrumbs/")
def build_breadcrumbs(data: dict, db: Session = Depends(get_db)):
    current_path = data.get("current_path", "")
    result = {
        "options": [
            {
                "value": "Clientes",
                "href": "/customer",
                "active": True,
            },
        ]
    }
    if current_path:
        parts = current_path.split("/")[1:]
        if len(parts) == 1:
            if parts[0] == "customer":
                result = {
                    "options": [
                        {
                            "value": "Clientes",
                            "href": "/customer",
                            "active": True,
                        },
                    ]
                }
            else:
                result = {
                    "options": [
                        {
                            "value": "Contratos",
                            "href": "/contract",
                            "active": True,
                        },
                    ]
                }
            return result
        elif len(parts) == 2:
            for option in result["options"]:
                option["active"] = False
            if parts[0] == "customer":
                customer = crud.get_customer(db=db, model_id=parts[1])
                next_option = {
                    "value": customer.name,
                    "href": "/customer/{}".format(customer.id),
                    "active": True,
                }
                result["options"].append(next_option)
            elif parts[0] == "file":
                file = crud.get_file(db=db, model_id=parts[1])
                invoice = crud.get_invoice(db=db, model_id=file.invoice_id)
                customer = crud.get_customer(db=db, model_id=invoice.customer_id)
                next_option = {
                    "value": customer.name,
                    "href": "/customer/{}".format(customer.id),
                    "active": False,
                }
                result["options"].append(next_option)
                next_option = {
                    "value": "Factura {}".format(invoice.number_id),
                    "href": "/invoice/{}".format(invoice.id),
                    "active": False,
                }
                result["options"].append(next_option)
                next_option = {
                    "value": "Contratos",
                    "href": "/file/{}".format(file.id),
                    "active": True,
                }
                result["options"].append(next_option)
            elif parts[0] == "invoice":
                invoice = crud.get_invoice(db=db, model_id=parts[1])
                customer = crud.get_customer(db=db, model_id=invoice.customer_id)
                next_option = {
                    "value": customer.name,
                    "href": "/customer/{}".format(customer.id),
                    "active": False,
                }
                result["options"].append(next_option)
                next_option = {
                    "value": "Factura {}".format(invoice.number_id),
                    "href": "/invoice/{}".format(invoice.id),
                    "active": True,
                }
                result["options"].append(next_option)
            return result
    return result


@api.get("/global/{global_name}", response_model=schemas.Global)
def get_global(global_name: str, db: Session = Depends(get_db)):
    return crud.get_global(db=db, global_name=global_name)


@api.get("/global/", response_model=list[schemas.Global])
def get_globals(db: Session = Depends(get_db)):
    return crud.get_globals(db=db)


@api.patch("/global/{model_id}", response_model=list[schemas.Global])
def update_global(model: dict, model_id: int, db: Session = Depends(get_db)):
    model["updated"] = datetime.now()
    result = crud.patch_global(db=db, model_id=model_id, update_dict=model)
    if result:
        return crud.get_globals(db=db)
    else:
        return []


@api.get("/service/", response_model=List[schemas.Service])
def get_services(db: Session = Depends(get_db)):
    return crud.get_services(db=db)


@api.post("/bill_to/", response_model=schemas.BillTo)
def create_bill_to(model: schemas.BillToCreate, db: Session = Depends(get_db)):
    return crud.create_billto(db=db, model=model)


@api.get("/bill_to/", response_model=list[schemas.BillTo])
def get_billtos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_billtos(db=db, skip=skip, limit=limit)


@api.delete("/bill_to/{model_id}", status_code=status.HTTP_200_OK)
def delete_bill_to(model_id: int, db: Session = Depends(get_db)):
    return crud.delete_billto(db=db, model_id=model_id)


@api.get("/topinfo/", response_model=list[schemas.TopInfo])
def get_topinfos(db: Session = Depends(get_db)):
    return crud.get_topinfos(db=db)


@api.patch("/topinfo/{model_id}", response_model=list[schemas.TopInfo])
def update_topinfo(model: dict, model_id: int, db: Session = Depends(get_db)):
    result = crud.patch_topinfo(db=db, model_id=model_id, update_dict=model)
    if result:
        return crud.get_topinfos(db=db)
    else:
        return None
