"""Tests for InMemoryAccountRepository"""

import pytest

from src.account import PersonalAccount
from src.repositories.memory_repository import InMemoryAccountRepository


@pytest.fixture
def memory_repo():
    """Fixture for InMemoryAccountRepository"""
    return InMemoryAccountRepository()


@pytest.fixture
def account_jan():
    """Fixture for test account"""
    return PersonalAccount("Jan", "Kowalski", 1000.0, "80010112345")


@pytest.fixture
def account_anna():
    """Fixture for test account"""
    return PersonalAccount("Anna", "Nowak", 2000.0, "90020212345")


class TestInMemoryAccountRepository:
    """Test suite for InMemoryAccountRepository"""

    def test_add_account(self, memory_repo, account_jan):
        """Test adding an account"""
        memory_repo.add(account_jan)
        assert memory_repo.count() == 1

    def test_find_by_pesel_found(self, memory_repo, account_jan):
        """Test finding an existing account"""
        memory_repo.add(account_jan)
        found = memory_repo.find_by_pesel("80010112345")
        assert found is not None
        assert found.first_name == "Jan"

    def test_find_by_pesel_not_found(self, memory_repo):
        """Test finding a non-existent account"""
        found = memory_repo.find_by_pesel("99999999999")
        assert found is None

    def test_get_all(self, memory_repo, account_jan, account_anna):
        """Test getting all accounts"""
        memory_repo.add(account_jan)
        memory_repo.add(account_anna)
        all_accounts = memory_repo.get_all()
        assert len(all_accounts) == 2

    def test_count(self, memory_repo, account_jan, account_anna):
        """Test counting accounts"""
        assert memory_repo.count() == 0
        memory_repo.add(account_jan)
        assert memory_repo.count() == 1
        memory_repo.add(account_anna)
        assert memory_repo.count() == 2

    def test_update_account(self, memory_repo, account_jan):
        """Test updating an account"""
        memory_repo.add(account_jan)
        updated = memory_repo.update("80010112345", first_name="Janusz")
        assert updated is not None
        assert updated.first_name == "Janusz"

    def test_update_account_last_name(self, memory_repo, account_jan):
        """Test updating account last name"""
        memory_repo.add(account_jan)
        updated = memory_repo.update("80010112345", last_name="Nowak")
        assert updated is not None
        assert updated.last_name == "Nowak"

    def test_update_nonexistent_account(self, memory_repo):
        """Test updating a non-existent account returns None"""
        updated = memory_repo.update("99999999999", first_name="Test")
        assert updated is None

    def test_delete_account(self, memory_repo, account_jan):
        """Test deleting an account"""
        memory_repo.add(account_jan)
        result = memory_repo.delete("80010112345")
        assert result is True
        assert memory_repo.count() == 0

    def test_delete_nonexistent_account(self, memory_repo):
        """Test deleting a non-existent account returns False"""
        result = memory_repo.delete("99999999999")
        assert result is False

    def test_clear(self, memory_repo, account_jan, account_anna):
        """Test clearing all accounts"""
        memory_repo.add(account_jan)
        memory_repo.add(account_anna)
        memory_repo.clear()
        assert memory_repo.count() == 0

    def test_save_all(self, memory_repo, account_jan, account_anna):
        """Test saving all accounts"""
        accounts = [account_jan, account_anna]
        count = memory_repo.save_all(accounts)
        assert count == 2
        assert memory_repo.count() == 2

    def test_save_all_empty(self, memory_repo):
        """Test saving empty list"""
        count = memory_repo.save_all([])
        assert count == 0
        assert memory_repo.count() == 0

    def test_save_all_replaces_existing(self, memory_repo, account_jan, account_anna):
        """Test that save_all replaces existing accounts"""
        # Add some accounts first
        memory_repo.add(account_jan)
        assert memory_repo.count() == 1

        # Save different accounts
        new_accounts = [account_anna]
        count = memory_repo.save_all(new_accounts)
        assert count == 1
        assert memory_repo.count() == 1

        # Verify old account is gone, new one is there
        assert memory_repo.find_by_pesel("80010112345") is None
        assert memory_repo.find_by_pesel("90020212345") is not None

    def test_load_all(self, memory_repo, account_jan, account_anna):
        """Test loading all accounts"""
        memory_repo.add(account_jan)
        memory_repo.add(account_anna)
        loaded = memory_repo.load_all()
        assert len(loaded) == 2
        assert any(acc.pesel == "80010112345" for acc in loaded)
        assert any(acc.pesel == "90020212345" for acc in loaded)

    def test_load_all_returns_copy(self, memory_repo, account_jan):
        """Test that load_all returns a copy, not original list"""
        memory_repo.add(account_jan)
        loaded = memory_repo.load_all()

        # Modify the loaded list
        loaded.clear()

        # Original should still have accounts
        assert memory_repo.count() == 1
