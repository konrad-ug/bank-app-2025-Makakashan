from unittest.mock import patch

import pytest

from src.account import BusinessAccount, PersonalAccount


@pytest.fixture
def personal_account():
    return PersonalAccount("Jan", "Kowalski", 100.0, "06241114012")


@pytest.fixture
def business_account():
    with patch("src.account.requests.get") as mock_get:
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"subject": {"nip": "1234567890", "statusVat": "Czynny"}}
        }
        account = BusinessAccount("Test Corp", "1234567890")
        account.balance = 100.0
        return account


def test_incoming_transfer(personal_account):
    personal_account.incoming_transfer(50.0)
    assert personal_account.balance == 150.0
    assert personal_account.historia == [50.0]


def test_outgoing_transfer_success(personal_account):
    personal_account.outgoing_transfer(50.0)
    assert personal_account.balance == 50.0
    assert personal_account.historia == [-50.0]


def test_outgoing_transfer_insufficient_funds(personal_account):
    personal_account.outgoing_transfer(150.0)
    assert personal_account.balance == 100.0
    assert personal_account.historia == []


@pytest.mark.parametrize(
    #
    "transfer_amount, expected_balance, expected_history",
    [
        (50.0, 49.0, [-50.0, -1.0]),
        (100.0, -1.0, [-100.0, -1.0]),
        (101.0, 100.0, []),
    ],
)
def test_express_transfer_personal(
    personal_account, transfer_amount, expected_balance, expected_history
):
    personal_account.express_transfer(transfer_amount)
    assert personal_account.balance == expected_balance
    assert personal_account.historia == expected_history


@pytest.mark.parametrize(
    #
    "transfer_amount, expected_balance, expected_history",
    [
        (50.0, 45.0, [-50.0, -5.0]),
        (100.0, -5.0, [-100.0, -5.0]),
        (101.0, 100.0, []),
    ],
)
def test_express_transfer_business(
    business_account, transfer_amount, expected_balance, expected_history
):
    business_account.express_transfer(transfer_amount)
    assert business_account.balance == expected_balance
    assert business_account.historia == expected_history


def test_history_example(personal_account):
    personal_account.balance = 0.0
    personal_account.historia = []

    personal_account.incoming_transfer(500.0)
    personal_account.express_transfer(300.0)

    assert personal_account.balance == 199.0
    assert personal_account.historia == [500.0, -300.0, -1.0]
