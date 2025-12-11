import pytest

from src.account import PersonalAccount
from src.registry import AccountRegistry, DuplicatePeselError


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
