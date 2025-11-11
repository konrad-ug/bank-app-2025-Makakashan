from src.account import BusinessAccount


class TestBusinessAccount:
    def test_business_account_creation(self):
        account = BusinessAccount("Firma XYZ", "1234567890")
        assert account.company_name == "Firma XYZ"
        assert account.nip == "1234567890"
        assert account.balance == 0.0
        assert account.historia == []

    def test_business_account_nip_validation_invalid(self):
        account_short = BusinessAccount("Firma Krótka", "123")
        assert account_short.nip == "Invalid"
        account_long = BusinessAccount("Firma Długa", "12345678901")
        assert account_long.nip == "Invalid"

    def test_business_account_nip_validation_valid(self):
        account = BusinessAccount("Firma Poprawna", "0987654321")
        assert account.nip == "0987654321"

    def test_business_account_no_promo_bonus(self):
        account = BusinessAccount("Firma z Kodem", "1234567890", "PROM_123")
        assert account.balance == 0.0
        assert account.historia == []
