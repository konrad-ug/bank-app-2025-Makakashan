from src.account import BusinessAccount, PersonalAccount


class TestTransfers:
    def test_incoming_transfer(self):
        account = PersonalAccount("Jan", "Kowalski", 100.0, "06241114012")
        account.incoming_transfer(50.0)
        assert account.balance == 150.0
        assert account.historia == [50.0]

    def test_outgoing_transfer_success(self):
        account = PersonalAccount("Jan", "Kowalski", 100.0, "06241114012")
        account.outgoing_transfer(50.0)
        assert account.balance == 50.0
        assert account.historia == [-50.0]

    def test_outgoing_transfer_insufficient_funds(self):
        account = PersonalAccount("Jan", "Kowalski", 100.0, "06241114012")
        account.outgoing_transfer(150.0)
        assert account.balance == 100.0
        assert account.historia == []

    def test_express_transfer_personal_account(self):
        account = PersonalAccount("Jan", "Kowalski", 100.0, "06241114012")
        account.express_transfer(50.0)
        assert account.balance == 49.0
        assert account.historia == [-50.0, -1.0]

    def test_express_transfer_business_account(self):
        account = BusinessAccount("Test Corp", "1234567890")
        account.balance = 100.0
        account.express_transfer(50.0)
        assert account.balance == 45.0
        assert account.historia == [-50.0, -5.0]

    def test_express_transfer_personal_account_on_limit(self):
        account = PersonalAccount("Jan", "Kowalski", 100.0, "06241114012")
        account.express_transfer(100.0)
        assert account.balance == -1.0
        assert account.historia == [-100.0, -1.0]

    def test_express_transfer_business_account_on_limit(self):
        account = BusinessAccount("Test Corp", "1234567890")
        account.balance = 100.0
        account.express_transfer(100.0)
        assert account.balance == -5.0
        assert account.historia == [-100.0, -5.0]

    def test_express_transfer_personal_insufficient_funds(self):
        account = PersonalAccount("Jan", "Kowalski", 100.0, "06241114012")
        account.express_transfer(101.0)
        assert account.balance == 100.0
        assert account.historia == []

    def test_express_transfer_business_insufficient_funds(self):
        account = BusinessAccount("Test Corp", "1234567890")
        account.balance = 100.0
        account.express_transfer(101.0)
        assert account.balance == 100.0
        assert account.historia == []

    def test_history_example(self):
        account = PersonalAccount("Jan", "Kowalski", 0.0, "06241114012")
        account.incoming_transfer(500.0)
        account.express_transfer(300.0)
        assert account.historia == [500.0, -300.0, -1.0]
