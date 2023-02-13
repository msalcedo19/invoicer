import os
import socket
import logging
from typing import Union
from config import LOG_LEVEL
from fastapi import FastAPI

api = FastAPI()
logging.basicConfig(format="[%(asctime)s] %(levelname)-8s - %(message)s", level=LOG_LEVEL)
log = logging.getLogger(__name__)

@api.get("/")
def read_root():
    return {"Hello": "World"}


@api.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@api.get()
def status():
    """Returns a detailed status of the service including all dependencies"""
    # TODO: Should replace this with database connection / service checks
    return {"status": "OK"}
