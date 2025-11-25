import pytest

from src.account import BusinessAccount


@pytest.fixture
def business_account():
    return BusinessAccount("Test Corp", "1234567890")


@pytest.mark.parametrize(
    "balance, history, loan_amount, expected_result, expected_balance",
    [
        (4000.0, [-1775, 500, 200], 2000.0, True, 6000.0),
        (3999.0, [-1775, 500], 2000.0, False, 3999.0),
        (4000.0, [1000, 500], 2000.0, False, 4000.0),
        (100.0, [100, 200], 1000.0, False, 100.0),
        (2000.0, [5000, -1775, -1000], 1000.0, True, 3000.0),
    ],
)
def test_take_loan(
    business_account,  # Используем фикстуру
    balance,
    history,
    loan_amount,
    expected_result,
    expected_balance,
):
    business_account.balance = balance
    business_account.historia = history

    granted = business_account.take_loan(loan_amount)

    assert granted is expected_result
    assert business_account.balance == expected_balance
