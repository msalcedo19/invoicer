from datetime import datetime, timedelta

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ms_invoicer.api import get_db
from ms_invoicer.security_helper import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user,
)
from ms_invoicer.sql_app import crud, schemas
from ms_invoicer.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()


@router.post("/authenticate", response_model=schemas.Token)
def authenticate(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


class PasswordCheckRequest(BaseModel):
    user_password: str


@router.post("/user/check_password")
def check_password(
    request: PasswordCheckRequest,
    current_user: schemas.User = Depends(get_current_user),
):
    user = authenticate_user(current_user.username, request.user_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Incorrect password",
        )
    return {"message": "correct password"}


@router.post("/user", response_model=schemas.User)
def create_user(model: dict, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db=db, username=model["username"])
    if not user:
        model["hashpass"] = get_password_hash(model["password"])
        model["created"] = datetime.now()
        model["updated"] = datetime.now()
        del model["password"]
    return crud.create_user(db=db, model=schemas.UserCreate(**model))
