import pytest
from mongomock import MongoClient

from src.account import PersonalAccount
from src.repositories.mongo_repository import MongoAccountsRepository


@pytest.fixture
def mongo_repo():
    """Create a MongoAccountsRepository with mongomock client"""
    client = MongoClient()
    repo = MongoAccountsRepository(
        client=client,
        database_name="test_bank_app",
        collection_name="accounts",
    )
    yield repo
    repo.clear()
    client.close()


@pytest.fixture
def account_jan():
    return PersonalAccount("Jan", "Kowalski", 100.0, "80010112345")


@pytest.fixture
def account_anna():
    return PersonalAccount("Anna", "Nowak", 200.0, "90020254321")


@pytest.fixture
def account_piotr():
    return PersonalAccount("Piotr", "Wiśniewski", 300.0, "85050598765")


class TestMongoAccountRepository:
    """Tests for MongoDB repository implementation"""

    def test_add_account(self, mongo_repo, account_jan):
        """Test adding an account to MongoDB"""
        mongo_repo.add(account_jan)

        assert mongo_repo.count() == 1
        found = mongo_repo.find_by_pesel("80010112345")
        assert found is not None
        assert found.first_name == "Jan"
        assert found.last_name == "Kowalski"
        assert found.pesel == "80010112345"

    def test_add_multiple_accounts(
        self, mongo_repo, account_jan, account_anna, account_piotr
    ):
        """Test adding multiple accounts"""
        mongo_repo.add(account_jan)
        mongo_repo.add(account_anna)
        mongo_repo.add(account_piotr)

        assert mongo_repo.count() == 3

    def test_find_by_pesel_found(self, mongo_repo, account_jan, account_anna):
        """Test finding an account by PESEL when it exists"""
        mongo_repo.add(account_jan)
        mongo_repo.add(account_anna)

        found = mongo_repo.find_by_pesel("90020254321")
        assert found is not None
        assert found.first_name == "Anna"
        assert found.last_name == "Nowak"
        assert found.balance == 200.0

    def test_find_by_pesel_not_found(self, mongo_repo, account_jan):
        """Test finding an account by PESEL when it doesn't exist"""
        mongo_repo.add(account_jan)

        found = mongo_repo.find_by_pesel("99999999999")
        assert found is None

    def test_get_all_accounts(self, mongo_repo, account_jan, account_anna):
        """Test retrieving all accounts"""
        mongo_repo.add(account_jan)
        mongo_repo.add(account_anna)

        accounts = mongo_repo.get_all()
        assert len(accounts) == 2
        pesels = [acc.pesel for acc in accounts]
        assert "80010112345" in pesels
        assert "90020254321" in pesels

    def test_get_all_empty(self, mongo_repo):
        """Test retrieving all accounts when repository is empty"""
        accounts = mongo_repo.get_all()
        assert accounts == []

    def test_count_accounts(self, mongo_repo, account_jan, account_anna, account_piotr):
        """Test counting accounts"""
        assert mongo_repo.count() == 0

        mongo_repo.add(account_jan)
        assert mongo_repo.count() == 1

        mongo_repo.add(account_anna)
        assert mongo_repo.count() == 2

        mongo_repo.add(account_piotr)
        assert mongo_repo.count() == 3

    def test_update_account_first_name(self, mongo_repo, account_jan):
        """Test updating account first name"""
        mongo_repo.add(account_jan)

        updated = mongo_repo.update("80010112345", first_name="Janusz")
        assert updated is not None
        assert updated.first_name == "Janusz"
        assert updated.last_name == "Kowalski"

        # Verify persistence
        found = mongo_repo.find_by_pesel("80010112345")
        assert found.first_name == "Janusz"

    def test_update_account_last_name(self, mongo_repo, account_jan):
        """Test updating account last name"""
        mongo_repo.add(account_jan)

        updated = mongo_repo.update("80010112345", last_name="Kowalewski")
        assert updated is not None
        assert updated.first_name == "Jan"
        assert updated.last_name == "Kowalewski"

    def test_update_account_both_names(self, mongo_repo, account_jan):
        """Test updating both first and last names"""
        mongo_repo.add(account_jan)

        updated = mongo_repo.update(
            "80010112345", first_name="Janusz", last_name="Kowalewski"
        )
        assert updated is not None
        assert updated.first_name == "Janusz"
        assert updated.last_name == "Kowalewski"

    def test_update_nonexistent_account(self, mongo_repo):
        """Test updating an account that doesn't exist"""
        updated = mongo_repo.update("99999999999", first_name="Test")
        assert updated is None

    def test_update_with_no_changes(self, mongo_repo, account_jan):
        """Test updating with both parameters None returns existing account"""
        mongo_repo.add(account_jan)
        updated = mongo_repo.update("80010112345", first_name=None, last_name=None)
        assert updated is not None
        assert updated.first_name == "Jan"
        assert updated.last_name == "Kowalski"

    def test_delete_account(self, mongo_repo, account_jan, account_anna):
        """Test deleting an account"""
        mongo_repo.add(account_jan)
        mongo_repo.add(account_anna)

        assert mongo_repo.count() == 2

        result = mongo_repo.delete("80010112345")
        assert result is True
        assert mongo_repo.count() == 1

        found = mongo_repo.find_by_pesel("80010112345")
        assert found is None

    def test_delete_nonexistent_account(self, mongo_repo, account_jan):
        """Test deleting an account that doesn't exist"""
        mongo_repo.add(account_jan)

        result = mongo_repo.delete("99999999999")
        assert result is False
        assert mongo_repo.count() == 1

    def test_clear_all_accounts(
        self, mongo_repo, account_jan, account_anna, account_piotr
    ):
        """Test clearing all accounts"""
        mongo_repo.add(account_jan)
        mongo_repo.add(account_anna)
        mongo_repo.add(account_piotr)

        assert mongo_repo.count() == 3

        mongo_repo.clear()
        assert mongo_repo.count() == 0
        assert mongo_repo.get_all() == []

    def test_account_with_history_preserved(self, mongo_repo):
        """Test that account history is preserved in MongoDB"""
        account = PersonalAccount("Jan", "Kowalski", 1000.0, "80010112345")
        account.incoming_transfer(500)
        account.outgoing_transfer(100)

        mongo_repo.add(account)

        found = mongo_repo.find_by_pesel("80010112345")
        assert found is not None
        assert found.historia == [500, -100]
        assert found.balance == 1400.0

    def test_account_with_promo_code_preserved(self, mongo_repo):
        """Test that promo code is preserved in MongoDB"""
        account = PersonalAccount(
            "Jan", "Kowalski", 1000.0, "65010112345", promo_code="PROM_123"
        )

        mongo_repo.add(account)

        found = mongo_repo.find_by_pesel("65010112345")
        assert found is not None
        assert found.promo_code == "PROM_123"

    def test_account_balance_preserved_after_update(self, mongo_repo):
        """Test that balance is preserved when updating account"""
        account = PersonalAccount("Jan", "Kowalski", 1000.0, "80010112345")
        account.incoming_transfer(500)
        mongo_repo.add(account)

        # Update name
        mongo_repo.update("80010112345", first_name="Janusz")

        # Balance should remain unchanged
        found = mongo_repo.find_by_pesel("80010112345")
        assert found.balance == 1500.0
        assert found.historia == [500]

    def test_duplicate_pesel_raises_error(self, mongo_repo, account_jan):
        """Test that adding duplicate PESEL raises an error"""
        mongo_repo.add(account_jan)

        # Try to add another account with same PESEL
        duplicate = PersonalAccount("Anna", "Nowak", 200.0, "80010112345")

        with pytest.raises(Exception):  # MongoDB will raise DuplicateKeyError
            mongo_repo.add(duplicate)

        # Only first account should be in database
        assert mongo_repo.count() == 1

    def test_empty_repository_operations(self, mongo_repo):
        """Test operations on empty repository"""
        assert mongo_repo.count() == 0
        assert mongo_repo.get_all() == []
        assert mongo_repo.find_by_pesel("12345678901") is None
        assert mongo_repo.delete("12345678901") is False
        assert mongo_repo.update("12345678901", first_name="Test") is None

    def test_account_to_dict_conversion(self, mongo_repo):
        """Test account serialization to dictionary"""
        account = PersonalAccount(
            "Jan", "Kowalski", 1000.0, "80010112345", promo_code="PROM_123"
        )
        account.incoming_transfer(100)

        doc = mongo_repo._account_to_dict(account)

        assert doc["first_name"] == "Jan"
        assert doc["last_name"] == "Kowalski"
        assert doc["pesel"] == "80010112345"
        assert doc["promo_code"] == "PROM_123"
        assert doc["balance"] == 1100.0
        assert doc["historia"] == [100]

    def test_dict_to_account_conversion(self, mongo_repo):
        """Test account deserialization from dictionary"""
        doc = {
            "first_name": "Jan",
            "last_name": "Kowalski",
            "balance": 1500.0,
            "pesel": "80010112345",
            "promo_code": "PROM_123",
            "historia": [500, -100, 200],
        }

        account = mongo_repo._dict_to_account(doc)

        assert account.first_name == "Jan"
        assert account.last_name == "Kowalski"
        assert account.pesel == "80010112345"
        assert account.promo_code == "PROM_123"
        assert account.balance == 1500.0
        assert account.historia == [500, -100, 200]

    def test_multiple_operations_sequence(self, mongo_repo):
        """Test a sequence of multiple operations"""
        # Add accounts
        acc1 = PersonalAccount("Jan", "Kowalski", 1000.0, "80010112345")
        acc2 = PersonalAccount("Anna", "Nowak", 2000.0, "90020254321")
        mongo_repo.add(acc1)
        mongo_repo.add(acc2)

        assert mongo_repo.count() == 2

        # Update one
        mongo_repo.update("80010112345", first_name="Janusz")

        # Delete one
        mongo_repo.delete("90020254321")

        assert mongo_repo.count() == 1

        # Verify remaining account
        found = mongo_repo.find_by_pesel("80010112345")
        assert found.first_name == "Janusz"

        # Add another
        acc3 = PersonalAccount("Piotr", "Wiśniewski", 3000.0, "85050598765")
        mongo_repo.add(acc3)

        assert mongo_repo.count() == 2

    def test_save_all_empty_list(self, mongo_repo):
        """Test saving empty list returns 0"""
        count = mongo_repo.save_all([])
        assert count == 0
        assert mongo_repo.count() == 0

    def test_save_all_replaces_existing_accounts(
        self, mongo_repo, account_jan, account_anna, account_piotr
    ):
        """save_all should replace existing data and return saved count"""
        mongo_repo.add(account_jan)
        assert mongo_repo.count() == 1

        saved = mongo_repo.save_all([account_anna, account_piotr])

        assert saved == 2
        assert mongo_repo.count() == 2
        pesels = {acc.pesel for acc in mongo_repo.get_all()}
        assert pesels == {"90020254321", "85050598765"}

    def test_load_all_returns_all_accounts(self, mongo_repo, account_jan, account_anna):
        """load_all should return every stored account"""
        mongo_repo.save_all([account_jan, account_anna])

        loaded_accounts = mongo_repo.load_all()

        assert len(loaded_accounts) == 2
        pesels = {acc.pesel for acc in loaded_accounts}
        assert "80010112345" in pesels
        assert "90020254321" in pesels
