from typing import Union

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ms_invoicer.db_pool import get_db
from ms_invoicer.security_helper import get_current_user
from ms_invoicer.sql_app import crud, schemas

router = APIRouter()


@router.get("/contract/{model_id}", response_model=Union[schemas.Service, None])
def get_contract(
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_contract(db=db, model_id=model_id, current_user_id=current_user.id)


@router.get("/contract", response_model=list[schemas.Service])
def get_contracts(
    current_user: schemas.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud.get_contracts(
        db=db, skip=skip, limit=limit, current_user_id=current_user.id
    )


@router.patch("/contract/{model_id}", response_model=Union[schemas.Service, None])
def patch_contract(
    model_update: dict,
    model_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = crud.patch_contract(
        db=db,
        model_id=model_id,
        current_user_id=current_user.id,
        update_dict=model_update,
    )
    if result:
        return crud.get_contract(
            db=db, model_id=model_id, current_user_id=current_user.id
        )
    else:
        return None


@router.delete("/contract/{contract_id}", status_code=status.HTTP_200_OK)
def delete_contract(
    contract_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.delete_contract(
        db=db, model_id=contract_id, current_user_id=current_user.id
    )


@router.post("/contract", response_model=schemas.Service)
def post_contract(
    contract: schemas.ServiceBase,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    obj_dict = contract.dict()
    obj_dict["user_id"] = current_user.id
    return crud.create_contract(db=db, model=schemas.ServiceCreate(**obj_dict))
