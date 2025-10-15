from src.account import Account


class TestAccount:
    def test_account_creation(self):
        account = Account("John", "Doe")
        assert account.first_name == "John"
        assert account.last_name == "Doe"
        assert account.balance == float(0.0)
        assert type(account.balance) is float
