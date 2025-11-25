import pytest

from src.account import BusinessAccount


class TestBusinessAccount:
    @pytest.mark.parametrize(
        #
        "company_name, nip, expected_nip",
        [
            ("Firma XYZ", "1234567890", "1234567890"),
            ("Firma Poprawna", "0987654321", "0987654321"),
            ("Firma Krótka", "123", "Invalid"),
            ("Firma Długa", "12345678901", "Invalid"),
            ("Firma Litery", "123456789A", "Invalid"),
        ],
    )
    def test_business_account_creation_and_nip(self, company_name, nip, expected_nip):
        account = BusinessAccount(company_name, nip)
        assert account.company_name == company_name
        assert account.nip == expected_nip
        assert account.balance == 0.0
        assert account.historia == []

    def test_business_account_no_promo_bonus(self):
        account = BusinessAccount("Firma z Kodem", "1234567890", "PROM_123")
        assert account.balance == 0.0
        assert account.historia == []
