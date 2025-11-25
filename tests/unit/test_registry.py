import pytest

from src.account import PersonalAccount
from src.registry import AccountRegistry


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
