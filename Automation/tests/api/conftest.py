import os
from typing import Generator
import pytest
import uuid
from playwright.sync_api import Playwright, APIRequestContext
from dotenv import load_dotenv

# Get data from .env
load_dotenv()
BASE_URL = os.getenv("BASE_URL")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

assert AUTH_TOKEN, "AUTH_TOKEN is not set"

# add and delete are candidates for helper functions but I'm keeping them here to simplify the framework
def add_employee(api_request_context, first_name: str, last_name: str) -> dict:
    payload = {
        "firstName": first_name,
        "lastName": last_name,
        "username": "Anything",
        "dependants": 0,
    }
    response = api_request_context.post("api/Employees", data=payload)
    return response.json()

def delete_employee(api_request_context, employee):
    api_request_context.delete(f"api/Employees/{employee['id']}")

@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright) -> Generator[APIRequestContext, None, None]:
    headers = {
        "Authorization": f"Basic {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    request_context = playwright.request.new_context(
        base_url=BASE_URL, extra_http_headers=headers
    )
    yield request_context
    request_context.dispose()

@pytest.fixture
def existing_employee(api_request_context):
    """
    Creates a new employee before the test runs, yields the first/last name.
    Entry is removed after test ends
    """ 

    first_name = f"Test{uuid.uuid4().hex[:8]}"
    last_name = f"User{uuid.uuid4().hex[:8]}"

    employee = add_employee(api_request_context, first_name, last_name)
    yield employee
    delete_employee(api_request_context, employee)