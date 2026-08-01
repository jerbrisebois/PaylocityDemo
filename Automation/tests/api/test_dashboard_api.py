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

    payload = {
        "id": existing_employee["id"],
        "firstName": new_first_name,
        "lastName": new_last_name,
        "username": "Anything",
        "dependants": 1,
    }
    response = api_request_context.put("api/Employees", data=payload)
    assert(response.status == 200)
    body = response.json()
    
    assert body["firstName"] == new_first_name
    assert body["lastName"] == new_last_name
    assert body["dependants"] == 1

def test_delete_employee_api(api_request_context, existing_employee):
    response = api_request_context.delete(f"api/Employees/{existing_employee['id']}")
    assert(response.status == 200)

    get_response = api_request_context.get(f"api/Employees/{existing_employee['id']}")

    body = get_response.text()
    assert body == ""