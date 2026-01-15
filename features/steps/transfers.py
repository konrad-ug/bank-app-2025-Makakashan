import requests
from behave import *

URL = "http://localhost:5000"


@when('I make an incoming transfer of "{amount}" to account with pesel: "{pesel}"')
def make_incoming_transfer(context, amount, pesel):
    json_body = {"amount": float(amount), "type": "incoming"}
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    assert response.status_code == 200, (
        f"Incoming transfer failed with status {response.status_code}"
    )


@when('I make an outgoing transfer of "{amount}" from account with pesel: "{pesel}"')
def make_outgoing_transfer(context, amount, pesel):
    json_body = {"amount": float(amount), "type": "outgoing"}
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    assert response.status_code == 200, (
        f"Outgoing transfer failed with status {response.status_code}"
    )


@when('I make an express transfer of "{amount}" from account with pesel: "{pesel}"')
def make_express_transfer(context, amount, pesel):
    json_body = {"amount": float(amount), "type": "express"}
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    assert response.status_code == 200, (
        f"Express transfer failed with status {response.status_code}"
    )


@when(
    'I try to make an outgoing transfer of "{amount}" from account with pesel: "{pesel}"'
)
def try_make_outgoing_transfer(context, amount, pesel):
    json_body = {"amount": float(amount), "type": "outgoing"}
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    context.last_transfer_status = response.status_code


@when(
    'I try to make an express transfer of "{amount}" from account with pesel: "{pesel}"'
)
def try_make_express_transfer(context, amount, pesel):
    json_body = {"amount": float(amount), "type": "express"}
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    context.last_transfer_status = response.status_code


@when(
    'I try to make an incoming transfer of "{amount}" to account with pesel: "{pesel}"'
)
def try_make_incoming_transfer(context, amount, pesel):
    json_body = {"amount": float(amount), "type": "incoming"}
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    context.last_transfer_status = response.status_code


@then('Transfer fails with status code "{status_code}"')
def check_transfer_failed_with_status(context, status_code):
    expected_status = int(status_code)
    actual_status = context.last_transfer_status
    assert actual_status == expected_status, (
        f"Expected transfer status {expected_status}, but got {actual_status}"
    )
