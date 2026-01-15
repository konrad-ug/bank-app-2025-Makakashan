import requests
from behave import *

URL = "http://localhost:5000"


@step(
    'I create an account using name: "{name}", last name: "{last_name}", pesel: "{pesel}"'
)
def create_account(context, name, last_name, pesel):
    json_body = {"name": f"{name}", "surname": f"{last_name}", "pesel": pesel}
    create_resp = requests.post(URL + "/api/accounts", json=json_body)
    assert create_resp.status_code == 201


@step("Account registry is empty")
def clear_account_registry(context):
    response = requests.get(URL + "/api/accounts")
    accounts = response.json()

    for account in accounts:
        pesel = account["pesel"]
        requests.delete(URL + f"/api/accounts/{pesel}")


@step('Number of accounts in registry equals: "{count}"')
def is_account_count_equal_to(context, count):
    response = requests.get(URL + "/api/accounts/count")
    assert response.status_code == 200
    data = response.json()
    actual_count = data.get("count")
    assert actual_count == int(count), (
        f"Expected {count} accounts, but got {actual_count}"
    )


@step('Account with pesel "{pesel}" exists in registry')
def check_account_with_pesel_exists(context, pesel):
    response = requests.get(URL + f"/api/accounts/{pesel}")
    assert response.status_code == 200, f"Account with pesel {pesel} should exist"


@step('Account with pesel "{pesel}" does not exist in registry')
def check_account_with_pesel_does_not_exist(context, pesel):
    response = requests.get(URL + f"/api/accounts/{pesel}")
    assert response.status_code == 404, f"Account with pesel {pesel} should not exist"


@when('I delete account with pesel: "{pesel}"')
def delete_account(context, pesel):
    response = requests.delete(URL + f"/api/accounts/{pesel}")
    assert response.status_code == 200, f"Failed to delete account with pesel {pesel}"


@when('I update "{field}" of account with pesel: "{pesel}" to "{value}"')
def update_field(context, field, pesel, value):
    if field not in ["name", "surname"]:
        raise ValueError(f"Invalid field: {field}. Must be 'name' or 'surname'.")

    json_body = {f"{field}": f"{value}"}
    response = requests.put(URL + f"/api/accounts/{pesel}", json=json_body)
    assert response.status_code == 200, f"Failed to update {field} for pesel {pesel}"


@then('Account with pesel "{pesel}" has "{field}" equal to "{value}"')
def field_equals_to(context, pesel, field, value):
    response = requests.get(URL + f"/api/accounts/{pesel}")
    assert response.status_code == 200, f"Account with pesel {pesel} not found"

    account = response.json()

    # Handle different field names
    if field == "balance":
        actual_value = str(account.get("balance"))
        assert actual_value == value, (
            f"Expected {field} to be {value}, but got {actual_value}"
        )
    else:
        actual_value = account.get(field)
        assert actual_value == value, (
            f"Expected {field} to be {value}, but got {actual_value}"
        )


@when(
    'I try to create an account using name: "{name}", last name: "{last_name}", pesel: "{pesel}"'
)
def try_create_account(context, name, last_name, pesel):
    json_body = {"name": f"{name}", "surname": f"{last_name}", "pesel": pesel}
    create_resp = requests.post(URL + "/api/accounts", json=json_body)
    context.last_response_status = create_resp.status_code


@then('Account creation fails with status code "{status_code}"')
def check_creation_failed_with_status(context, status_code):
    expected_status = int(status_code)
    actual_status = context.last_response_status
    assert actual_status == expected_status, (
        f"Expected status {expected_status}, but got {actual_status}"
    )
