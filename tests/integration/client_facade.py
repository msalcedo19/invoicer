import gzip
import json
from abc import abstractmethod
from typing import Any, Dict

import requests

"""
This module is meant to abstract the type of client used for testing.
FastAPI's TestClient works directly against the api.py module, bypassing
HTTP. This allows changing what type of client implementation is used
for testing purposes.
"""


class ResponseFacade:
    def __init__(self, status_code: int):
        self.status_code = status_code

    @abstractmethod
    def json(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def text(self) -> str:
        pass

    @abstractmethod
    def data(self) -> bytes:
        pass

    def headers(self) -> Dict[str, str]:
        pass


class ClientFacade:
    @abstractmethod
    async def get(
        self, path, headers: Dict[str, str] = None, params: Dict[str, str] = None
    ) -> ResponseFacade:
        pass

    @abstractmethod
    async def delete(
        self,
        path,
        headers: Dict[str, str] = None,
        json: Dict[str, Any] = None,
        params: Dict[str, str] = None,
        data: bytes = None,
    ) -> ResponseFacade:
        pass

    @abstractmethod
    async def post(
        self,
        path,
        headers: Dict[str, str] = None,
        params: Dict[str, str] = None,
        json: Dict[str, Any] = None,
        data: bytes = None,
    ) -> ResponseFacade:
        pass

    @abstractmethod
    async def put(
        self,
        path,
        headers: Dict[str, str] = None,
        params: Dict[str, str] = None,
        json: Dict[str, Any] = None,
        data: bytes = None,
    ) -> ResponseFacade:
        pass

    @abstractmethod
    async def patch(
        self,
        path,
        headers: Dict[str, str] = None,
        params: Dict[str, str] = None,
        json: Dict[str, Any] = None,
        data: bytes = None,
    ) -> ResponseFacade:
        pass


class HttpResponseFace(ResponseFacade):
    def __init__(self, response, has_payload=True):
        super(HttpResponseFace, self).__init__(response.status_code)
        self.response = response
        self.has_payload = has_payload

    def json(self) -> Dict[str, Any]:
        return self.response.json() if self.has_payload else None

    def text(self) -> str:
        return self.response.text

    def data(self) -> bytes:
        return self.response.content

    def headers(self) -> Dict[str, str]:
        return self.response.headers


class HttpClientFacade(ClientFacade):
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url if not base_url.endswith("/") else base_url[:-1]

    @staticmethod
    def actual_path(path: str) -> str:
        if path is None or len(path) == 0:
            return "/"
        elif not path.startswith("/"):
            return f"/{path}"
        return path

    async def get(
        self, path, headers: Dict[str, str] = None, params: Dict[str, str] = None
    ) -> ResponseFacade:
        response = requests.get(
            f"{self.base_url}{HttpClientFacade.actual_path(path)}", headers=headers, params=params
        )
        return HttpResponseFace(response)

    async def delete(
        self,
        path,
        headers: Dict[str, str] = None,
        json: Dict[str, Any] = None,
        params: Dict[str, str] = None,
        data: bytes = None,
    ) -> ResponseFacade:
        full_path = f"{self.base_url}{HttpClientFacade.actual_path(path)}"
        if data:
            response = requests.delete(full_path, data=data, headers=headers)
        elif json:
            response = requests.delete(full_path, json=json, headers=headers)
        else:
            response = requests.delete(full_path, params=params, headers=headers)

        return HttpResponseFace(response, has_payload=False)

    async def post(
        self,
        path,
        headers: Dict[str, str] = None,
        params: Dict[str, str] = None,
        json: Dict[str, Any] = None,
        data: bytes = None,
    ) -> ResponseFacade:
        full_path = f"{self.base_url}{HttpClientFacade.actual_path(path)}"
        if data:
            response = requests.post(full_path, headers=headers, params=params, data=data)
        else:
            response = requests.post(full_path, headers=headers, params=params, json=json)

        return HttpResponseFace(response)

    async def put(
        self,
        path,
        headers: Dict[str, str] = None,
        params: Dict[str, str] = None,
        json: Dict[str, Any] = None,
        data: bytes = None,
    ) -> ResponseFacade:
        full_path = f"{self.base_url}{HttpClientFacade.actual_path(path)}"
        if data:
            response = requests.put(full_path, headers=headers, data=data, params=params)
        else:
            response = requests.put(full_path, headers=headers, json=json, params=params)
        return HttpResponseFace(response)

    async def patch(
        self,
        path,
        headers: Dict[str, str] = None,
        params: Dict[str, str] = None,
        json: Dict[str, Any] = None,
        data: bytes = None,
    ) -> ResponseFacade:
        full_path = f"{self.base_url}{HttpClientFacade.actual_path(path)}"
        if data:
            response = requests.patch(full_path, headers=headers, data=data, params=params)
        else:
            response = requests.patch(full_path, headers=headers, json=json, params=params)
        return HttpResponseFace(response)
