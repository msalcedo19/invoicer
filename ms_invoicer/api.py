import logging
from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from ms_invoicer.config import LOG_LEVEL
from ms_invoicer.db_pool import get_db
from ms_invoicer.event_handler import register_event_handlers
from ms_invoicer.routers import bill_to, customer, files, invoice, user
from ms_invoicer.security_helper import get_current_user
from ms_invoicer.sql_app import crud, schemas
from ms_invoicer.utils import create_folders
from ms_invoicer.no_upload_helper import populate_db
from ms_invoicer.dao import PdfToProcessEvent
from ms_invoicer.event_bus import publish
from pydantic import BaseModel

create_folders()
populate_db()

api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
api.include_router(customer.router, tags=["Customer"])
api.include_router(invoice.router, tags=["Invoice"])
api.include_router(files.router, tags=["File"])
api.include_router(bill_to.router, tags=["Bill_to"])
api.include_router(user.router, tags=["User"])

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


@api.post("/breadcrumbs")
def build_breadcrumbs(
    data: dict,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_path = data.get("current_path", None)
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
            return result
        elif len(parts) == 2:
            for option in result["options"]:
                option["active"] = False
            if parts[0] == "customer":
                customer = crud.get_customer(
                    db=db, model_id=parts[1], current_user_id=current_user.id
                )
                next_option = {
                    "value": customer.name,
                    "href": "/customer/{}".format(customer.id),
                    "active": True,
                }
                result["options"].append(next_option)
            elif parts[0] == "files":
                file = crud.get_file(
                    db=db, model_id=parts[1], current_user_id=current_user.id
                )
                invoice = crud.get_invoice(
                    db=db, model_id=file.invoice_id, current_user_id=current_user.id
                )
                customer = crud.get_customer(
                    db=db, model_id=invoice.customer_id, current_user_id=current_user.id
                )
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
                    "href": "/files/{}".format(file.id),
                    "active": True,
                }
                result["options"].append(next_option)
            elif parts[0] == "invoice":
                invoice = crud.get_invoice(
                    db=db, model_id=parts[1], current_user_id=current_user.id
                )
                customer = crud.get_customer(
                    db=db, model_id=invoice.customer_id, current_user_id=current_user.id
                )
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


@api.get("/global/{identifier}", response_model=schemas.Global)
def get_global(
    identifier: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_global(
        db=db, identifier=identifier, current_user_id=current_user.id
    )


@api.get("/global", response_model=list[schemas.Global])
def get_globals(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_globals(db=db, current_user_id=current_user.id)


@api.patch("/global/{model_id}", response_model=list[schemas.Global])
def update_global(
    model: dict,
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    model["updated"] = datetime.now()
    global_var = crud.get_global_by_id(
        db=db, model_id=model_id, current_user_id=current_user.id
    )
    if global_var and (global_var.identifier == 1 or global_var.identifier == 2):
        model["value"] = model["value"].replace(",", ".")
    result = crud.patch_global(
        db=db, model_id=model_id, current_user_id=current_user.id, update_dict=model
    )
    if result:
        return crud.get_globals(db=db, current_user_id=current_user.id)
    else:
        return []


@api.get("/service", response_model=List[schemas.Service])
def get_services(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_services(db=db, current_user_id=current_user.id)


@api.post("/service", response_model=List[schemas.Service])
def post_service(
    contracts: List[schemas.ServiceCreate],
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = []
    for contract in contracts:
        obj_dict = contract.dict()
        obj_dict["user_id"] = current_user.id
        result.append(
            crud.create_service(db=db, model=schemas.ServiceCreate(**obj_dict))
        )
    return result


@api.get("/topinfo", response_model=list[schemas.TopInfo])
def get_topinfos(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_topinfos(db=db, current_user_id=current_user.id)


@api.patch("/topinfo/{model_id}", response_model=list[schemas.TopInfo])
def update_topinfo(
    model: dict,
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = crud.patch_topinfo(
        db=db, model_id=model_id, current_user_id=current_user.id, update_dict=model
    )
    if result:
        return crud.get_topinfos(db=db, current_user_id=current_user.id)
    else:
        return None


class Generate_PDF(BaseModel):
    bill_to_id: str
    invoice: schemas.InvoiceBase
    contracts: List[schemas.ServiceCreateNoFile]
    use_existing_invoice: bool = False
    with_taxes: bool = True


@api.post("/generate_pdf")
async def generate_pdf(
    body: Generate_PDF,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = crud.get_invoices_by_number_id(
        db=db,
        number_id=body.invoice.number_id,
        customer_id=body.invoice.customer_id,
        current_user_id=current_user.id,
    )
    if not result or body.use_existing_invoice:
        try:
            if result and body.use_existing_invoice:
                new_invoice = result
            else:
                obj_dict = body.invoice.dict()
                obj_dict["user_id"] = current_user.id
                new_invoice = crud.create_invoice(
                    db=db, model=schemas.InvoiceCreate(**obj_dict)
                )
            file_obj = schemas.FileCreate(
                **{
                    "s3_xlsx_url": None,
                    "s3_pdf_url": None,
                    "created": datetime.now(),
                    "invoice_id": new_invoice.id,
                    "bill_to_id": body.bill_to_id,
                    "user_id": current_user.id,
                }
            )
            new_file = crud.create_file(db=db, model=file_obj)
            result = []
            for contract in body.contracts:
                obj_dict = contract.dict()
                obj_dict["user_id"] = current_user.id
                obj_dict["invoice_id"] = new_invoice.id
                obj_dict["file_id"] = new_file.id
                result.append(
                    crud.create_service(db=db, model=schemas.ServiceCreate(**obj_dict))
                )
            template_name = "template01.html"
            if not body.with_taxes:
                template_name = "template03.html"
            data_event = PdfToProcessEvent(
                current_user_id=current_user.id,
                invoice=new_invoice,
                file=new_file,
                html_template_name=template_name,
                xlsx_url=None,
                with_file=False,
                with_taxes=body.with_taxes
            )
            log.info("Customer {} - Publishing pdf event".format(current_user.id))
            await publish(data_event)
            return crud.get_file(
                db=db, model_id=new_file.id, current_user_id=current_user.id
            )
        except Exception as e:
            log.error("Customer {} - {}".format(current_user.id, e))
            files = crud.get_files_by_invoice(
                db=db, model_id=new_invoice.id, current_user_id=current_user.id
            )
            for file in files:
                crud.delete_services_by_file(
                    db=db, model_id=file.id, current_user_id=current_user.id
                )
            crud.delete_files_by_invoice(
                db=db, model_id=new_invoice.id, current_user_id=current_user.id
            )
            crud.delete_invoice(
                db=db, model_id=new_invoice.id, current_user_id=current_user.id
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Existe una factura con ese numéro de factura",
        )


@api.get("/template", response_model=list[schemas.Template])
def get_templates(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_templates(db=db, current_user_id=current_user.id)
