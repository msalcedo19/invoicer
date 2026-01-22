import json
import os
import time
from typing import Callable

from ms_invoicer.utils import BreadCrumbs


CACHE_DIR = "temp/cache"
#TODO: Probar expiracion
CACHE_EXPIRY_SECONDS = 3600*24*7  # Example: 1 week


def cache_key(key: str) -> str:
    return os.path.join(CACHE_DIR, f"{key}.json")


def is_cache_valid(file_path: str) -> bool:
    if not os.path.exists(file_path):
        return False
    if time.time() - os.path.getmtime(file_path) > CACHE_EXPIRY_SECONDS:
        return False
    return True


def read_cache(file_path: str) -> BreadCrumbs:
    with open(file_path, 'r') as file:
        data_json = json.load(file)
        return BreadCrumbs(**json.loads(data_json))


def write_cache(file_path: str, data: BreadCrumbs) -> None:
    with open(file_path, 'w') as file:
        json.dump(str(data), file)


def get_cached_data(key: str, fetch_function: Callable[[], BreadCrumbs]) -> BreadCrumbs:
    file_path = cache_key(key)
    if is_cache_valid(file_path):
        return read_cache(file_path)
    data = fetch_function()
    write_cache(file_path, data)
    return data
