import logging
from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError
from sqlalchemy.orm import Session

from ms_invoicer.config import LOG_LEVEL
from ms_invoicer.db_pool import get_db
from ms_invoicer.event_handler import register_event_handlers
from ms_invoicer.routers import bill_to, contract, customer, files, invoice, user
from ms_invoicer.security_helper import get_current_user, get_payload_from_header
from ms_invoicer.sql_app import crud, schemas
from ms_invoicer.utils import create_folders

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
api.include_router(files.router, tags=["File"])
api.include_router(bill_to.router, tags=["Bill_to"])
api.include_router(user.router, tags=["User"])

logging.basicConfig(
    format="[%(asctime)s] %(levelname)-8s - %(message)s", level=LOG_LEVEL
)
log = logging.getLogger(__name__)
register_event_handlers()

EXCLUDED_ENDPOINTS_FROM_AUTH = ["/authenticate", "/docs", "/openapi.json", "/"]


@api.middleware("http")
async def check_token(request: Request, call_next):
    try:
        if request.url.path not in EXCLUDED_ENDPOINTS_FROM_AUTH:
            get_payload_from_header(request.headers.get("authorization", None))
        response = await call_next(request)
        return response
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    except ExpiredSignatureError:
        return JSONResponse(
            content={"error": "Invalid credentials"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


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


@api.get("/global/{global_name}", response_model=schemas.Global)
def get_global(
    global_name: str,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_global(
        db=db, global_name=global_name, current_user_id=current_user.id
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
