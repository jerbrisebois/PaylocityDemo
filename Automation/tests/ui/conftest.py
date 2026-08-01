# tests/ui/conftest.py

import os
import uuid
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

# Get data from .env
load_dotenv()
BASE_URL = os.getenv("BASE_URL")
UI_USERNAME = os.getenv("UI_USERNAME")
UI_PASSWORD = os.getenv("UI_PASSWORD")

@pytest.fixture
def page(page: Page):
    """
    Override the default 'page' to automatically login.
    """
    page.goto(BASE_URL)
    page.locator("#Username").fill(UI_USERNAME)
    page.locator("#Password").fill(UI_PASSWORD)
    page.get_by_role("button", name="Log In").click()
    # Ensure the javascript has finished executing
    page.wait_for_load_state("networkidle")
    expect(page).to_have_title("Employees - Paylocity Benefits Dashboard")
    return page

# Note: I'm not actually using this, just wanted to show how I'd handle testing
# the login screen since I overrode Page above
@pytest.fixture
def logged_out_page(context):
    """
    Unauthenticated page for scenarios where testing pre-login is required
    """
    page = context.new_page()
    page.goto(BASE_URL)
    return page

@pytest.fixture
def existing_employee(page: Page):
    """
    Creates a new employee before the test runs, yields the first/last name.
    Entry is removed after test ends
    """ 

    employee = add_employee(page)
    yield employee
    delete_employee(page, employee)

def add_employee(page: Page) -> dict:
    first_name = f"Test{uuid.uuid4().hex[:8]}"
    last_name = f"User{uuid.uuid4().hex[:8]}"

    page.get_by_role("button", name="Add Employee").click()
    page.locator("#firstName").fill(first_name)
    page.locator("#lastName").fill(last_name)
    page.locator("#dependants").fill("0")
    page.locator("#addEmployee").click()

    row = page.locator("#employeesTable tr", has_text=first_name)
    expect(row).to_be_visible()
    employee_id = row.locator("td").nth(0).inner_text()

    return {"id": employee_id, "first_name": first_name, "last_name": last_name}

def delete_employee(page: Page, employee: dict):
    row = page.locator("#employeesTable tr", has_text=employee["id"])
    if row.count() > 0:
        row.locator(".fa-times").click()
        page.get_by_role("button", name="Delete").click()
        expect(row).to_have_count(0)