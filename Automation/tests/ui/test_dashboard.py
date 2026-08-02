import uuid
import pytest
from playwright.sync_api import Page, expect
from conftest import add_employee, delete_employee

def test_add_employee(page: Page):
    employee = add_employee(page)
    try:
        row = page.locator("#employeesTable tr", has_text=employee["first_name"])
        expect(row).to_be_visible()
        expect(row).to_contain_text(employee["last_name"])
    finally:
        delete_employee(page, employee)

def test_edit_employee_last_name(page: Page, existing_employee):
    row = page.locator("#employeesTable tr", has_text=existing_employee["first_name"])
    row.locator(".fa-edit").click()

    new_last_name = f"Edit_lastname_{uuid.uuid4().hex[:8]}"
    page.locator("#lastName").fill(new_last_name)
    page.locator("#updateEmployee").click()

    updated_row = page.locator("#employeesTable tr", has_text=existing_employee["first_name"])
    expect(updated_row).to_contain_text(new_last_name)

def test_edit_employee_data(page: Page, existing_employee):
    row = page.locator("#employeesTable tr", has_text=existing_employee["first_name"])
    row.locator(".fa-edit").click()

    new_first_name = f"Edit_data_{uuid.uuid4().hex[:8]}"
    new_last_name = f"Edit_data_{uuid.uuid4().hex[:8]}"
    page.locator("#firstName").fill(new_first_name)
    page.locator("#lastName").fill(new_last_name)
    page.locator("#dependants").fill("1")
    page.locator("#updateEmployee").click()

    updated_row = page.locator("#employeesTable tr", has_text=new_first_name)
    expect(updated_row).to_contain_text(new_last_name)
    dependents_cell = updated_row.locator("td").nth(3)
    expect(dependents_cell).to_have_text("1")

def test_delete_employee(page: Page, existing_employee):
    row = page.locator("#employeesTable tr", has_text=existing_employee["first_name"])
    row.locator(".fa-times").click()
    page.get_by_role("button", name="Delete").click()

    expect(row).to_have_count(0)

@pytest.mark.parametrize("dependants", [0, 4, 32])
def test_benefits_cost(page: Page, dependants):
    employee = add_employee(page, dependants = str(dependants))
    try:
        expected_cost = (1000 + (500 * dependants)) / 26
        row = page.locator("#employeesTable tr", has_text=employee["id"])
        benefits_cost_cell = row.locator("td").nth(6)
        expect(benefits_cost_cell).to_have_text(f"{expected_cost:.2f}")
    finally:
        delete_employee(page, employee)

def test_xss_input(page: Page):
    fired_dialogs = []

    # Capture and close a dialogue if it pops up during this test
    def handle_dialog(dialog):
        fired_dialogs.append(dialog.message)
        dialog.dismiss()
    page.on("dialog", handle_dialog)

    rows = page.locator("#employeesTable tr")
    initial_count = rows.count()
    all_employee_ids = set(page.locator("#employeesTable td:nth-child(1)").all_inner_texts())

    page.get_by_role("button", name="Add Employee").click()
    page.locator("#firstName").fill("<img src=x onerror=alert(1)>")
    page.locator("#lastName").fill(f"XssTest{uuid.uuid4().hex[:8]}")
    page.locator("#dependants").fill("0")

    # Force waiting for the dialogue to popup when clicking "Add"
    # There may be a better way to handle this as this will hide a legitimate timeout
    try:
        with page.expect_event("dialog", timeout=2000):
            page.locator("#addEmployee").click()
    except TimeoutError:
        pass

    new_all_employee_ids = set(page.locator("#employeesTable td:nth-child(1)").all_inner_texts())
    new_employee_id = (new_all_employee_ids - all_employee_ids).pop()
    
    try:
        assert len(fired_dialogs) == 0, "XSS payload executed - input was not sanitized"
    finally:
        row = page.locator("#employeesTable tr", has_text=new_employee_id)
        #row.locator(".fa-times").click()
        #page.get_by_role("button", name="Delete").click()
        #expect(row).to_have_count(0)