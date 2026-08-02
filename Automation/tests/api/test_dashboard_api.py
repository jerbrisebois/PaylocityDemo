import os
import pytest
import uuid
from playwright.sync_api import Playwright, APIRequestContext
from dotenv import load_dotenv
from conftest import add_employee, delete_employee

def test_add_employee_api(api_request_context):
    first_name = f"Test{uuid.uuid4().hex[:8]}"
    last_name = f"User{uuid.uuid4().hex[:8]}"
    id = None

    try:
        employee = add_employee(api_request_context, first_name, last_name)

        id = employee["id"]
        assert employee["firstName"] == first_name
        assert employee["lastName"] == last_name
        assert employee["dependants"] == 0
    finally:
        if id:
            delete_employee(api_request_context, employee)

def test_edit_employee_lastname_api(api_request_context, existing_employee):
    new_last_name = f"User{uuid.uuid4().hex[:8]}"

    payload = {
        "id": existing_employee["id"],
        "firstName": existing_employee["firstName"],
        "lastName": new_last_name,
        "username": "Anything",
        "dependants": 0,
    }
    response = api_request_context.put("api/Employees", data=payload)
    assert(response.status == 200)
    body = response.json()
    
    assert body["firstName"] == existing_employee["firstName"]
    assert body["lastName"] == new_last_name
    assert body["dependants"] == 0

def test_edit_employee_data_api(api_request_context, existing_employee):
    new_first_name = f"User{uuid.uuid4().hex[:8]}"
    new_last_name = f"User{uuid.uuid4().hex[:8]}"
    new_dependants = 1

    payload = {
        "id": existing_employee["id"],
        "firstName": new_first_name,
        "lastName": new_last_name,
        "username": "Anything",
        "dependants": new_dependants,
    }
    response = api_request_context.put("api/Employees", data=payload)
    assert(response.status == 200)
    body = response.json()
    
    assert body["firstName"] == new_first_name
    assert body["lastName"] == new_last_name
    assert body["dependants"] == new_dependants

def test_delete_employee_api(api_request_context, existing_employee):
    response = api_request_context.delete(f"api/Employees/{existing_employee['id']}")
    assert(response.status == 200)

    get_response = api_request_context.get(f"api/Employees/{existing_employee['id']}")

    body = get_response.text()
    assert body == ""

@pytest.mark.parametrize("dependants", [0, 4, 32])
def test_benefits_cost_api(api_request_context, dependants):
    dependants = 4
    payload = {
        "firstName": f"Test{uuid.uuid4().hex[:8]}",
        "lastName": f"User{uuid.uuid4().hex[:8]}",
        "username": "Anything",
        "dependants": dependants,
    }
    response = api_request_context.post("api/Employees", data=payload)
    assert response.status == 200
    body = response.json()

    try:
        expected_benefits_cost = (1000 + (500 * dependants)) / 26
        expected_net = (body["salary"] / 26) - expected_benefits_cost

        assert body["benefitsCost"] == pytest.approx(expected_benefits_cost, abs=0.01)
        assert body["net"] == pytest.approx(expected_net, abs=0.01)
    finally:
        api_request_context.delete(f"api/Employees/{body['id']}")

def test_update_nonexistent_employee(api_request_context):
    payload = {
        "firstName": f"Test{uuid.uuid4().hex[:8]}",
        "lastName": f"User{uuid.uuid4().hex[:8]}",
        "username": "Anything",
        "id": str(uuid.uuid4()),
        "salary": -1000
    }
    response = api_request_context.put("api/Employees", data=payload)

    try:
        # The response code we should get here is unclear, likely a 404 or 405
        # Simply checking that it is not a 200 for now
        assert response.status != 200
    finally:
        # This will not be needed once API bug 20 is fixed (the employee should never be created)
        # For now, it helps keep the environment clean although it does delete the evidence that
        # an employee created this way has a bogus salary/net pay.
        body = response.json()
        api_request_context.delete(f"api/Employees/{body['id']}")