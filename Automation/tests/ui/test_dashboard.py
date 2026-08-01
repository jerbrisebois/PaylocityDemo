import uuid
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

def test_benefit_cost(page: Page, existing_employee):
    hi = 1