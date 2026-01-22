from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ms_invoicer.db_pool import get_db
from ms_invoicer.security_helper import get_current_user
from ms_invoicer.sql_app import crud, schemas
from ms_invoicer.utils import get_current_date

router = APIRouter()


@router.get("/global/{identifier}", response_model=schemas.Global)
def get_global(
    identifier: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Optional[schemas.Global]:
    return crud.get_global(
        db=db, identifier=identifier, current_user_id=current_user.id
    )


@router.get("/global", response_model=list[schemas.Global])
def get_globals(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[schemas.Global]:
    return crud.get_globals(db=db, current_user_id=current_user.id)


@router.patch("/global/{model_id}", response_model=list[schemas.Global])
def update_global(
    model: dict,
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[schemas.Global]:
    model["updated"] = get_current_date()
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
