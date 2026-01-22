from logging import getLogger

import pytest
from fastapi.testclient import TestClient

from ms_invoicer.api import api

LOG = getLogger(__name__)


@pytest.fixture()
def test_client():
    """Test client."""
    yield TestClient(api)
