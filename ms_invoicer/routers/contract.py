from typing import Union
import logging
from ms_invoicer.config import LOG_LEVEL
from fastapi import Depends, status, Form, APIRouter
from sqlalchemy.orm import Session
from ms_invoicer.sql_app import crud, schemas
from ms_invoicer.db_pool import get_db

router = APIRouter()


@router.get("/contract/{model_id}", response_model=Union[schemas.Service, None])
def get_contract(model_id: int, db: Session = Depends(get_db)):
    return crud.get_contract(db=db, model_id=model_id)


@router.get("/contract/", response_model=list[schemas.Service])
def get_contracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_contracts(db=db, skip=skip, limit=limit)


@router.patch("/contract/{model_id}", response_model=Union[schemas.Service, None])
def patch_contract(model_update: dict, model_id: int, db: Session = Depends(get_db)):
    result = crud.patch_contract(db=db, model_id=model_id, update_dict=model_update)
    if result:
        return crud.get_contract(db=db, model_id=model_id)
    else:
        return None


@router.delete("/contract/{contract_id}", status_code=status.HTTP_200_OK)
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    return crud.delete_contract(db=db, model_id=contract_id)


@router.post("/contract/", response_model=schemas.Service)
def post_contract(contract: schemas.ServiceCreate, db: Session = Depends(get_db)):
    return crud.create_contract(db=db, model=contract)
