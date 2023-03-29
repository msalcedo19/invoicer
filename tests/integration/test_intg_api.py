import pytest
from fastapi.testclient import TestClient

def test_customer(test_client: TestClient):
    payload = {
        "name": "customer1",
        "tax1": 5,
        "tax2": 10,
        "price_unit": 15
    }
    response = test_client.post("/customer", json=payload)
    assert response.status_code == 200
    result_id = response.json().get("id")
    assert result_id

    response = test_client.get("/customer/{}".format(result_id))
    assert response.status_code == 200
    (name, tax1, tax2, price_unit) = (
        response.json().get("name"), 
        response.json().get("tax1"), 
        response.json().get("tax2"), 
        response.json().get("price_unit")
    )
    assert name == "customer1"
    assert tax1 == 5
    assert tax2 == 10
    assert price_unit == 15

    payload = {
            "name": "customer1_changed",
    }
    response = test_client.patch("/customer/{}".format(result_id), json=payload)
    assert response.status_code == 200
    name = response.json().get("name")
    assert name == "customer1_changed"

    response = test_client.delete("/customer/{}".format(result_id))
    assert response.status_code == 200
    assert response.json() == 1

    response = test_client.get("/customer/{}".format(result_id))
    assert response.status_code == 200
    assert response.json() == None
