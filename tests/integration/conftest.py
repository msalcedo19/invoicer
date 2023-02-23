import pytest
from logging import getLogger
from ms_invoicer.api import api
from fastapi.testclient import TestClient

LOG = getLogger(__name__)


@pytest.fixture()
def test_client():
    yield TestClient(api)
