import pytest

from src.account import PersonalAccount


@pytest.fixture
def basic_account_details():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "balance": 0.0,
    }


class TestAccount:
    def test_account_creation(self, basic_account_details):
        account = PersonalAccount(**basic_account_details, pesel="06241114012")
        assert account.first_name == "John"
        assert account.last_name == "Doe"
        assert type(account.balance) is float
        assert account.historia == []

    def test_account_pesel(self, basic_account_details):
        account = PersonalAccount(
            **basic_account_details, pesel="06241114012", promo_code="PROM_12345"
        )
        assert len(account.pesel) == 11
        assert account.pesel.isdigit()

    @pytest.mark.parametrize(
        #
        "pesel, promo_code, expected_balance, expected_history",
        [
            ("60241114012", "PROM_123", 50.0, [50]),
            ("06241114012", "PROM_123", 0.0, []),
            ("06241114012", None, 0.0, []),
            ("06241114012", "INVALID", 0.0, []),
            ("06241114012", "PROM_1234", 0.0, []),
            ("06241114012", "PROM_123456", 0.0, []),
            ("123", "PROM_123", 0.0, []),  # Short PESEL - should not get promo
        ],
    )
    def test_account_promo_code_logic(
        self,
        basic_account_details,
        pesel,
        promo_code,
        expected_balance,
        expected_history,
    ):
        account = PersonalAccount(
            **basic_account_details, pesel=pesel, promo_code=promo_code
        )

        assert account.promo_code == promo_code
        assert account.balance == expected_balance
        assert account.historia == expected_history
