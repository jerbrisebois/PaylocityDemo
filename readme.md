# Paylocity Benefits Dashboard — Test Automation

Automated UI and API test suites for the Benefits Dashboard, built with Python, pytest, and Playwright.


## Prerequisites

- Python 3.x
- Access credentials for the application (see Configuration below)


## Setup

1. Clone this repo and navigate to the Automation directory

`cd Automation`

2. Create and activate a python virtual environment

`python -m venv venv`

2a. Run the activation script appropriate to your environment

`.\venv\Scripts\Activate.ps1` (PowerShell)

Note: If you receive the error "Activate.ps1 cannot be loaded because running scripts is disabled on this system" the following command must be run first:

`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

`.\venv\Scripts\Activate.bat` (Windows CMD prompt)

`source .venv/bin/activate` (macOS / Linux - Bash / Zsh)

`source .venv/bin/activate.fish` (macOS / Linux - Fish Shell)

`source .venv/bin/activate.csh` (macOS / Linux - Csh / Tcsh)

`overlay use .venv/bin/activate.nu` (Nushell)


3. Install dependencies

`pip install -r requirements.txt`

`playwright install`

4. .env configuration - Copy/paste the `.env.example` to `.env` and fill in credentials. For the API key omit the "Basic "


## Running the tests

Run everything with `pytest`

Run only UI tests with `pytest tests/ui`

Add `--headed` to this to show the browser execution (ex: `pytest tests/ui --headed`)

Run only API tests with `pytest tests/api`

Run single test example: `pytest tests/ui/test_dashboard.py::test_add_employee`

To generate a report.html after the tests are done, add `--html=report.html --self-contained-html` (ex: `pytest --html=report.html --self-contained-html`)

For more verbose output, add `-v`


## List of tests

### UI

test_add_employee - Add an employee and verify it exists

test_edit_employee_lastname - Edit an employee's last name and verify it's been updated

test_edit_employee_data - Edit an employee's first and last name and depentents and verify it's been updated

test_delete_employee - Delete an employee and verify it has been removed

test_benefits_cost - Add 3 different employees with different dependent amounts and verify the benefit cost calculation for each

test_xss_input - Add an employee with xss input used in the name field and verify it does not execute 

### API

test_add_employee_api - Send a POST to /api/Employees to create a new employee and verify it is created

test_edit_employee_lastname_api - Send a PUT to /api/Employees to edit an existing employee's last name and verify it's been updated

test_edit_employee_data_api - Send a PUT to /api/Employees to edit an employee's first and last name and depentents and verify it's been updated

test_delete_employee_api - Send a DEL to /api/Employees/{id} to delete an employee and verify it has been removed

test_benefits_cost_api - Send a POST to /api/Employees with 3 different dependent amounts, verifying the benefit cost calculation for each

test_update_nonexistent_employee - Send a PUT to /api/Employees to edit a non-existent employee and verify the request is not processed

## Design Notes

- Test data is self-contained. Each test will create its own prerequisite data, act only upon it and delete it after the test concludes
- The "page" fixture is overridden, so each test will, by default, log in prior to executing the test. I have included a specific fixture (logged_out_page) that could be used when writing tests on the login screen (though I have not included any as that seemed outside the scope of the project)


## Related documentation

- [UI Bug Report](PaylocityDemoUIBugReport.md)
- [API Bug Report](PaylocityDemoAPIBugReport.md)
