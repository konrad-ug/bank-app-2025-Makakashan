from src.account import PersonalAccount


class TestAccount:
    def test_account_creation(self):
        account = PersonalAccount("John", "Doe", 0.0, "06241114012")
        assert account.first_name == "John"
        assert account.last_name == "Doe"
        assert type(account.balance) is float
        assert account.historia == []

    def test_account_pesel(self):
        account = PersonalAccount("John", "Doe", 0.0, "06241114012", "PROM_12345")
        assert len(account.pesel) == 11
        assert account.pesel.isdigit()

    def test_account_promo_code(self):
        account = PersonalAccount("John", "Doe", 0.0, "60241114012", "PROM_123")
        assert account.promo_code == "PROM_123"
        assert account.balance == 50.0
        assert account.historia == [50]

    def test_account_promo_code_2(self):
        account = PersonalAccount("John", "Doe", 0.0, "06241114012", "PROM_123")
        assert account.promo_code == "PROM_123"
        assert account.balance == 0.0
        assert account.historia == []

    def test_account_promo_code_none(self):
        account = PersonalAccount("John", "Doe", 0.0, "06241114012")
        assert account.promo_code is None
        assert account.balance == 0.0
        assert account.historia == []

    def test_account_promo_code_invalid(self):
        account = PersonalAccount("John", "Doe", 0.0, "06241114012", "INVALID")
        assert account.promo_code == "INVALID"
        assert account.balance == 0.0
        assert account.historia == []

    def test_account_promo_code_invalid_length(self):
        account = PersonalAccount("John", "Doe", 0.0, "06241114012", "PROM_1234")
        assert account.promo_code == "PROM_1234"
        assert account.balance == 0.0
        assert account.historia == []

    def test_account_promo_code_invalid_format(self):
        account = PersonalAccount("John", "Doe", 0.0, "06241114012", "PROM_123456")
        assert account.promo_code == "PROM_123456"
        assert account.balance == 0.0
        assert account.historia == []
