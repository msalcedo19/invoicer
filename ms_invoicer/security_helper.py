from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ms_invoicer.config import ALGORITHM, SECRET_KEY
from ms_invoicer.db_pool import get_db
from ms_invoicer.sql_app import crud, schemas

# Use PBKDF2 to avoid bcrypt backend issues under Python 3.12.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="authenticate/")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_payload_from_header(authorization: str = Header(...)):
    if not authorization:
        raise HTTPException(status_code=400, detail="Authorization header missing")
    # check that the Authorization header starts with Bearer
    if "bearer" not in authorization.lower():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme")
    # Extract the token from the Authorization header
    token = authorization.split("bearer ")[1]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
        user = crud.get_user_by_username(db=db, username=token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def authenticate_user(username: str, password: str, db: Session):
    user = crud.get_user_by_username(db=db, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashpass):
        return False
    return user
