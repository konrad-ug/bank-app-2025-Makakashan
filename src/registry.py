from typing import Optional

from src.account import PersonalAccount
from src.repositories import AccountRepositoryInterface
from src.repositories.memory_repository import InMemoryAccountRepository


class DuplicatePeselError(Exception):
    """Exception raised when attempting to add account with duplicate PESEL"""

    def __init__(self, pesel: str):
        self.pesel = pesel
        super().__init__(f"Account with PESEL {pesel} already exists")


class AccountRegistry:
    """Registry for managing personal accounts with pluggable storage backend"""

    def __init__(self, repository: Optional[AccountRepositoryInterface] = None):
        """
        Initialize AccountRegistry with a repository.

        Args:
            repository: Storage backend implementation. If None, uses InMemoryAccountRepository
        """
        if repository is None:
            repository = InMemoryAccountRepository()
        self._repository = repository

    def add_account(self, account: PersonalAccount) -> None:
        """
        Add a new account to the registry.

        Args:
            account: PersonalAccount to add

        Raises:
            DuplicatePeselError: If an account with the same PESEL already exists
        """
        # Check if account with this PESEL already exists
        if self.find_account_by_pesel(account.pesel) is not None:
            raise DuplicatePeselError(account.pesel)
        self._repository.add(account)

    def find_account_by_pesel(self, pesel: str) -> Optional[PersonalAccount]:
        """
        Find an account by PESEL.

        Args:
            pesel: PESEL number to search for

        Returns:
            PersonalAccount if found, None otherwise
        """
        return self._repository.find_by_pesel(pesel)

    def get_all_accounts(self) -> list[PersonalAccount]:
        """
        Get all accounts in the registry.

        Returns:
            List of all PersonalAccount objects
        """
        return self._repository.get_all()

    def get_account_count(self) -> int:
        """
        Get the total number of accounts in the registry.

        Returns:
            Number of accounts
        """
        return self._repository.count()

    def update_account(
        self,
        pesel: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Optional[PersonalAccount]:
        """
        Update account information.

        Args:
            pesel: PESEL of the account to update
            first_name: New first name (optional)
            last_name: New last name (optional)

        Returns:
            Updated PersonalAccount if found, None otherwise
        """
        return self._repository.update(pesel, first_name, last_name)

    def delete_account(self, pesel: str) -> bool:
        """
        Delete an account by PESEL.

        Args:
            pesel: PESEL of the account to delete

        Returns:
            True if account was deleted, False if not found
        """
        return self._repository.delete(pesel)

    def clear_all_accounts(self) -> None:
        """Clear all accounts from the registry"""
        self._repository.clear()

    def save_accounts_to_repository(
        self, repository: Optional[AccountRepositoryInterface] = None
    ) -> int:
        """
        Save all accounts to the provided repository (defaults to current backend).

        Args:
            repository: Optional target repository for persistence.

        Returns:
            Number of accounts persisted.
        """
        target_repository = repository or self._repository
        accounts = self.get_all_accounts()
        return target_repository.save_all(accounts)

    def load_accounts_from_repository(
        self, repository: Optional[AccountRepositoryInterface] = None
    ) -> int:
        """
        Load accounts from the provided repository (defaults to current backend) and
        replace current registry state.

        Args:
            repository: Optional source repository to load accounts from.

        Returns:
            Number of accounts loaded into the registry.
        """
        source_repository = repository or self._repository
        accounts = source_repository.load_all()
        self.clear_all_accounts()
        for account in accounts:
            self._repository.add(account)
        return len(accounts)

    @property
    def accounts(self) -> list[PersonalAccount]:
        """
        Legacy property for backward compatibility.

        Returns:
            List of all accounts
        """
        return self.get_all_accounts()
