import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable, AsyncIterator, List, Optional

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from ms_invoicer.config import LOG_LEVEL
from ms_invoicer.constants import LogEvent
from ms_invoicer.db_pool import get_db
from ms_invoicer.sql_app.database import init_db
from ms_invoicer.event_handler import register_event_handlers
from ms_invoicer.routers import bill_to, customer, files, invoice, user, globals, utils
from ms_invoicer.security_helper import get_current_user
from ms_invoicer.sql_app import crud, schemas
from ms_invoicer.utils import create_folders

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Lifespan."""
    init_db()
    create_folders()
    register_event_handlers()
    yield


api = FastAPI(lifespan=lifespan)
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
api.include_router(globals.router, tags=["Globals"])
api.include_router(user.router, tags=["User"])
api.include_router(utils.router, tags=["Utils"])

logging.basicConfig(
    format="[%(asctime)s] %(levelname)-8s - %(message)s", level=LOG_LEVEL
)
log = logging.getLogger(__name__)


@api.middleware("http")
async def add_process_time_header(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Add process time header."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    log.info(
        "Request completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": int(process_time * 1000),
            "event": LogEvent.REQUEST_TIMING.value,
        },
    )
    return response


@api.get("/")
def api_status() -> dict[str, str]:
    """Return service status.

    Example response:
    {
      "status": "OK"
    }
    """
    # TODO: Should replace this with database connection / service checks
    return {"status": "OK"}


@api.get("/service", response_model=List[schemas.Service])
def get_services(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[schemas.Service]:
    """List services for the current user.

    Example request:
    GET /service
    """
    return crud.get_services(db=db, current_user_id=current_user.id)


@api.post("/service", response_model=List[schemas.Service])
def post_service(
    contracts: List[schemas.ServiceCreate],
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[schemas.Service]:
    """Create services in bulk.

    Example JSON:
    [
      {
        "title": "Service A",
        "amount": 100,
        "currency": "CAD",
        "hours": 2,
        "price_unit": 50,
        "file_id": 1,
        "invoice_id": 1
      }
    ]
    """
    result = []
    for contract in contracts:
        obj_dict = contract.model_dump()
        obj_dict["user_id"] = current_user.id
        result.append(
            crud.create_service(db=db, model=schemas.ServiceCreate(**obj_dict))
        )
    return result


@api.get("/topinfo", response_model=list[schemas.TopInfo])
def get_topinfos(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[schemas.TopInfo]:
    """Get top info records.

    Example request:
    GET /topinfo
    """
    return crud.get_topinfos(db=db, current_user_id=current_user.id)


@api.patch("/topinfo/{model_id}", response_model=list[schemas.TopInfo])
def update_topinfo(
    model: dict[str, Any],
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Optional[list[schemas.TopInfo]]:
    """Update top info.

    Example JSON:
    {
      "ti_from": "QUeBEC INC",
      "addr": "123 Main St",
      "phone": "+1 555-0100",
      "email": "info@example.com"
    }
    """
    result = crud.patch_topinfo(
        db=db, model_id=model_id, current_user_id=current_user.id, update_dict=model
    )
    if result:
        return crud.get_topinfos(db=db, current_user_id=current_user.id)
    else:
        return None


@api.get("/template", response_model=list[schemas.Template])
def get_templates(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[schemas.Template]:
    """List templates for the current user.

    Example request:
    GET /template
    """
    return crud.get_templates(db=db, current_user_id=current_user.id)
