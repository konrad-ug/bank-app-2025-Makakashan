from unittest.mock import MagicMock, Mock

import pytest

from src.account import PersonalAccount
from src.registry import AccountRegistry, DuplicatePeselError
from src.repositories import AccountRepositoryInterface
from src.repositories.memory_repository import InMemoryAccountRepository


@pytest.fixture
def registry():
    return AccountRegistry()


@pytest.fixture
def account_jan():
    return PersonalAccount("Jan", "Kowalski", 100.0, "80010112345")


@pytest.fixture
def account_anna():
    return PersonalAccount("Anna", "Nowak", 200.0, "90020254321")


class TestAccountRegistry:
    def test_registry_init(self, registry):
        assert registry.get_account_count() == 0
        assert registry.get_all_accounts() == []

    def test_add_account(self, registry, account_jan):
        registry.add_account(account_jan)
        assert registry.get_account_count() == 1
        assert registry.get_all_accounts() == [account_jan]

    def test_add_multiple_accounts(self, registry, account_jan, account_anna):
        registry.add_account(account_jan)
        registry.add_account(account_anna)
        assert registry.get_account_count() == 2
        assert registry.get_all_accounts() == [account_jan, account_anna]

    def test_find_account_by_pesel_found(self, registry, account_jan, account_anna):
        registry.add_account(account_jan)
        registry.add_account(account_anna)

        found_account = registry.find_account_by_pesel("80010112345")
        assert found_account == account_jan
        assert found_account.first_name == "Jan"

    def test_find_account_by_pesel_not_found(self, registry, account_jan):
        registry.add_account(account_jan)

        found_account = registry.find_account_by_pesel("11111111111")
        assert found_account is None

    def test_add_account_with_duplicate_pesel_raises_error(self, registry):
        """Test that adding account with duplicate PESEL raises DuplicatePeselError"""
        account1 = PersonalAccount("Jan", "Kowalski", 100.0, "80010112345")
        account2 = PersonalAccount("Anna", "Nowak", 200.0, "80010112345")

        registry.add_account(account1)

        with pytest.raises(DuplicatePeselError) as exc_info:
            registry.add_account(account2)

        assert exc_info.value.pesel == "80010112345"
        assert "80010112345" in str(exc_info.value)

    def test_add_account_duplicate_pesel_does_not_add_to_registry(self, registry):
        """Test that duplicate PESEL doesn't get added to registry"""
        account1 = PersonalAccount("Jan", "Kowalski", 100.0, "80010112345")
        account2 = PersonalAccount("Anna", "Nowak", 200.0, "80010112345")

        registry.add_account(account1)
        initial_count = registry.get_account_count()

        with pytest.raises(DuplicatePeselError):
            registry.add_account(account2)

        # Count should remain the same
        assert registry.get_account_count() == initial_count
        assert registry.get_account_count() == 1

        # Only first account should be in registry
        found = registry.find_account_by_pesel("80010112345")
        assert found.first_name == "Jan"
        assert found.last_name == "Kowalski"

    def test_add_accounts_with_different_pesels_succeeds(self, registry):
        """Test that adding accounts with different PESELs works fine"""
        account1 = PersonalAccount("Jan", "Kowalski", 100.0, "80010112345")
        account2 = PersonalAccount("Anna", "Nowak", 200.0, "90020254321")
        account3 = PersonalAccount("Piotr", "Wiśniewski", 300.0, "85050598765")

        registry.add_account(account1)
        registry.add_account(account2)
        registry.add_account(account3)

        assert registry.get_account_count() == 3

    def test_update_account_does_not_conflict_with_same_pesel(self, registry):
        """Test that updating account with same PESEL doesn't raise error"""
        account = PersonalAccount("Jan", "Kowalski", 100.0, "80010112345")
        registry.add_account(account)

        # Update should work fine
        updated = registry.update_account("80010112345", first_name="Janusz")
        assert updated is not None
        assert updated.first_name == "Janusz"

    def test_delete_and_readd_with_same_pesel_succeeds(self, registry):
        """Test that after deleting account, same PESEL can be used again"""
        account1 = PersonalAccount("Jan", "Kowalski", 100.0, "80010112345")
        registry.add_account(account1)

        # Delete the account
        registry.delete_account("80010112345")

        # Should be able to add new account with same PESEL
        account2 = PersonalAccount("Anna", "Nowak", 200.0, "80010112345")
        registry.add_account(account2)

        assert registry.get_account_count() == 1
        found = registry.find_account_by_pesel("80010112345")
        assert found.first_name == "Anna"


class TestAccountRegistryWithMockedRepository:
    """Tests for AccountRegistry using mocked repository"""

    def test_registry_with_custom_repository(self):
        """Test that registry accepts custom repository"""
        mock_repo = MagicMock(spec=AccountRepositoryInterface)
        mock_repo.count.return_value = 0
        mock_repo.get_all.return_value = []

        registry = AccountRegistry(repository=mock_repo)

        assert registry.get_account_count() == 0
        assert registry.get_all_accounts() == []

    def test_add_account_calls_repository(self):
        """Test that add_account calls repository.add()"""
        mock_repo = MagicMock(spec=AccountRepositoryInterface)
        mock_repo.find_by_pesel.return_value = None  # No duplicate

        registry = AccountRegistry(repository=mock_repo)
        account = PersonalAccount("Jan", "Kowalski", 100.0, "80010112345")

        registry.add_account(account)

        mock_repo.add.assert_called_once_with(account)

    def test_add_account_checks_for_duplicates(self):
        """Test that add_account checks for duplicate PESEL"""
        mock_repo = MagicMock(spec=AccountRepositoryInterface)
        existing_account = PersonalAccount("Jan", "Kowalski", 100.0, "80010112345")
        mock_repo.find_by_pesel.return_value = existing_account

        registry = AccountRegistry(repository=mock_repo)
        duplicate = PersonalAccount("Anna", "Nowak", 200.0, "80010112345")

        with pytest.raises(DuplicatePeselError):
            registry.add_account(duplicate)

        # Repository add should not be called for duplicate
        mock_repo.add.assert_not_called()

    def test_find_account_by_pesel_calls_repository(self):
        """Test that find_account_by_pesel calls repository"""
        mock_repo = MagicMock(spec=AccountRepositoryInterface)
        account = PersonalAccount("Jan", "Kowalski", 100.0, "80010112345")
        mock_repo.find_by_pesel.return_value = account

        registry = AccountRegistry(repository=mock_repo)
        found = registry.find_account_by_pesel("80010112345")

        mock_repo.find_by_pesel.assert_called_once_with("80010112345")
        assert found == account

    def test_get_all_accounts_calls_repository(self):
        """Test that get_all_accounts calls repository"""
        mock_repo = MagicMock(spec=AccountRepositoryInterface)
        accounts = [
            PersonalAccount("Jan", "Kowalski", 100.0, "80010112345"),
            PersonalAccount("Anna", "Nowak", 200.0, "90020254321"),
        ]
        mock_repo.get_all.return_value = accounts

        registry = AccountRegistry(repository=mock_repo)
        result = registry.get_all_accounts()

        mock_repo.get_all.assert_called_once()
        assert result == accounts

    def test_get_account_count_calls_repository(self):
        """Test that get_account_count calls repository"""
        mock_repo = MagicMock(spec=AccountRepositoryInterface)
        mock_repo.count.return_value = 5

        registry = AccountRegistry(repository=mock_repo)
        count = registry.get_account_count()

        mock_repo.count.assert_called_once()
        assert count == 5

    def test_update_account_calls_repository(self):
        """Test that update_account calls repository"""
        mock_repo = MagicMock(spec=AccountRepositoryInterface)
        updated_account = PersonalAccount("Janusz", "Kowalski", 100.0, "80010112345")
        mock_repo.update.return_value = updated_account

        registry = AccountRegistry(repository=mock_repo)
        result = registry.update_account("80010112345", first_name="Janusz")

        mock_repo.update.assert_called_once_with("80010112345", "Janusz", None)
        assert result == updated_account

    def test_delete_account_calls_repository(self):
        """Test that delete_account calls repository"""
        mock_repo = MagicMock(spec=AccountRepositoryInterface)
        mock_repo.delete.return_value = True

        registry = AccountRegistry(repository=mock_repo)
        result = registry.delete_account("80010112345")

        mock_repo.delete.assert_called_once_with("80010112345")
        assert result is True

    def test_clear_all_accounts_calls_repository(self):
        """Test that clear_all_accounts calls repository"""
        mock_repo = MagicMock(spec=AccountRepositoryInterface)

        registry = AccountRegistry(repository=mock_repo)
        registry.clear_all_accounts()

        mock_repo.clear.assert_called_once()

    def test_save_accounts_to_repository_with_external_repo(self):
        """Test that save_accounts_to_repository delegates to provided repository"""
        registry = AccountRegistry()
        registry.add_account(PersonalAccount("Jan", "Kowalski", 100.0, "80010112345"))
        registry.add_account(PersonalAccount("Anna", "Nowak", 200.0, "90020254321"))

        external_repo = MagicMock(spec=AccountRepositoryInterface)
        external_repo.save_all.return_value = 2

        saved_count = registry.save_accounts_to_repository(external_repo)

        assert saved_count == 2
        external_repo.save_all.assert_called_once()
        args, _ = external_repo.save_all.call_args
        assert len(args[0]) == 2

    def test_load_accounts_from_repository_replaces_state(self):
        """Test that load_accounts_from_repository loads accounts from the source repo"""
        registry = AccountRegistry()
        source_repo = MagicMock(spec=AccountRepositoryInterface)
        loaded_accounts = [
            PersonalAccount("Piotr", "Wisniewski", 300.0, "85050598765"),
            PersonalAccount("Ewa", "Kowal", 150.0, "75010112345"),
        ]
        source_repo.load_all.return_value = loaded_accounts

        count = registry.load_accounts_from_repository(source_repo)

        assert count == 2
        assert registry.get_account_count() == 2
        assert {acc.pesel for acc in registry.get_all_accounts()} == {
            "85050598765",
            "75010112345",
        }
        source_repo.load_all.assert_called_once()

    def test_accounts_property_backward_compatibility(self):
        """Test that accounts property works for backward compatibility"""
        mock_repo = MagicMock(spec=AccountRepositoryInterface)
        accounts = [PersonalAccount("Jan", "Kowalski", 100.0, "80010112345")]
        mock_repo.get_all.return_value = accounts

        registry = AccountRegistry(repository=mock_repo)
        result = registry.accounts

        mock_repo.get_all.assert_called_once()
        assert result == accounts


class TestAccountRegistryWithMongoMock:
    """Integration tests for AccountRegistry with MongoDB using mongomock"""

    @pytest.fixture
    def mongo_registry(self):
        """Create AccountRegistry with mongomock-backed repository"""
        from mongomock import MongoClient

        from src.repositories.mongo_repository import MongoAccountsRepository

        client = MongoClient()
        repo = MongoAccountsRepository(
            client=client,
            database_name="test_bank_app",
            collection_name="accounts",
        )

        registry = AccountRegistry(repository=repo)
        yield registry

        # Cleanup
        repo.clear()
        client.close()

    def test_registry_with_mongo_add_and_find(self, mongo_registry):
        """Test adding and finding accounts with MongoDB backend"""
        account = PersonalAccount("Jan", "Kowalski", 1000.0, "80010112345")

        mongo_registry.add_account(account)

        found = mongo_registry.find_account_by_pesel("80010112345")
        assert found is not None
        assert found.first_name == "Jan"
        assert found.last_name == "Kowalski"
        assert found.balance == 1000.0

    def test_registry_with_mongo_duplicate_pesel(self, mongo_registry):
        """Test that MongoDB backend prevents duplicate PESELs"""
        account1 = PersonalAccount("Jan", "Kowalski", 100.0, "80010112345")
        account2 = PersonalAccount("Anna", "Nowak", 200.0, "80010112345")

        mongo_registry.add_account(account1)

        with pytest.raises(DuplicatePeselError):
            mongo_registry.add_account(account2)

    def test_registry_with_mongo_update(self, mongo_registry):
        """Test updating account with MongoDB backend"""
        account = PersonalAccount("Jan", "Kowalski", 1000.0, "80010112345")
        mongo_registry.add_account(account)

        updated = mongo_registry.update_account("80010112345", first_name="Janusz")
        assert updated is not None
        assert updated.first_name == "Janusz"

        # Verify persistence
        found = mongo_registry.find_account_by_pesel("80010112345")
        assert found.first_name == "Janusz"

    def test_registry_with_mongo_delete(self, mongo_registry):
        """Test deleting account with MongoDB backend"""
        account = PersonalAccount("Jan", "Kowalski", 1000.0, "80010112345")
        mongo_registry.add_account(account)

        result = mongo_registry.delete_account("80010112345")
        assert result is True

        found = mongo_registry.find_account_by_pesel("80010112345")
        assert found is None

    def test_registry_with_mongo_multiple_accounts(self, mongo_registry):
        """Test managing multiple accounts with MongoDB backend"""
        accounts = [
            PersonalAccount("Jan", "Kowalski", 100.0, "80010112345"),
            PersonalAccount("Anna", "Nowak", 200.0, "90020254321"),
            PersonalAccount("Piotr", "Wiśniewski", 300.0, "85050598765"),
        ]

        for account in accounts:
            mongo_registry.add_account(account)

        assert mongo_registry.get_account_count() == 3

        all_accounts = mongo_registry.get_all_accounts()
        assert len(all_accounts) == 3

        pesels = [acc.pesel for acc in all_accounts]
        assert "80010112345" in pesels
        assert "90020254321" in pesels
        assert "85050598765" in pesels

    def test_registry_with_mongo_history_preserved(self, mongo_registry):
        """Test that account history is preserved in MongoDB"""
        account = PersonalAccount("Jan", "Kowalski", 1000.0, "80010112345")
        account.incoming_transfer(500)
        account.outgoing_transfer(100)

        mongo_registry.add_account(account)

        found = mongo_registry.find_account_by_pesel("80010112345")
        assert found.historia == [500, -100]
        assert found.balance == 1400.0

    def test_registry_with_mongo_clear_all(self, mongo_registry):
        """Test clearing all accounts with MongoDB backend"""
        accounts = [
            PersonalAccount("Jan", "Kowalski", 100.0, "80010112345"),
            PersonalAccount("Anna", "Nowak", 200.0, "90020254321"),
        ]

        for account in accounts:
            mongo_registry.add_account(account)

        assert mongo_registry.get_account_count() == 2

        mongo_registry.clear_all_accounts()

        assert mongo_registry.get_account_count() == 0
        assert mongo_registry.get_all_accounts() == []
