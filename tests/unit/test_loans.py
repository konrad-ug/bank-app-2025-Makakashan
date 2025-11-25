import pytest

from src.account import PersonalAccount


@pytest.fixture
def personal_account():
    return PersonalAccount("Jan", "Kowalski", 100.0, "06241114012")


@pytest.mark.parametrize(
    "history, loan_amount, expected_result, expected_balance",
    [
        ([100, 200, 50], 500, True, 600.0),
        ([500, 500, -100, -50, 200], 1000, True, 1100.0),
        ([100, 200], 1000, False, 100.0),
        ([100, 100, -50, 100, -100], 200, False, 100.0),
        ([500, -100, -1.0, 300, 200], 800, True, 900.0),
        ([500, 500, -100, -50, 200], 1050, False, 100.0),
    ],
)
def test_submit_for_loan(
    personal_account, history, loan_amount, expected_result, expected_balance
):
    personal_account.historia = history
    initial_history_len = len(history)

    granted = personal_account.submit_for_loan(loan_amount)

    assert granted is expected_result
    assert personal_account.balance == expected_balance

    if expected_result:
        assert len(personal_account.historia) == initial_history_len + 1
        assert personal_account.historia[-1] == loan_amount
    else:
        assert len(personal_account.historia) == initial_history_len
