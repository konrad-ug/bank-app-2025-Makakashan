from typing import List, Optional

from src.account import PersonalAccount
from src.repositories import AccountRepositoryInterface


class InMemoryAccountRepository(AccountRepositoryInterface):
    """In-memory implementation of account repository"""

    def __init__(self):
        self._accounts: List[PersonalAccount] = []

    def add(self, account: PersonalAccount) -> None:
        """Add an account to the repository"""
        self._accounts.append(account)

    def find_by_pesel(self, pesel: str) -> Optional[PersonalAccount]:
        """Find an account by PESEL"""
        for account in self._accounts:
            if account.pesel == pesel:
                return account
        return None

    def get_all(self) -> List[PersonalAccount]:
        """Get all accounts"""
        return self._accounts.copy()

    def count(self) -> int:
        """Get the total number of accounts"""
        return len(self._accounts)

    def update(
        self,
        pesel: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Optional[PersonalAccount]:
        """Update an account"""
        account = self.find_by_pesel(pesel)
        if account is None:
            return None

        if first_name is not None:
            account.first_name = first_name
        if last_name is not None:
            account.last_name = last_name

        return account

    def delete(self, pesel: str) -> bool:
        """Delete an account by PESEL"""
        account = self.find_by_pesel(pesel)
        if account is None:
            return False

        self._accounts.remove(account)
        return True

    def clear(self) -> None:
        """Clear all accounts from the repository"""
        self._accounts.clear()

    def save_all(self, accounts: List[PersonalAccount]) -> int:
        """Persist all provided accounts, replacing existing data"""
        self._accounts = [account for account in accounts]
        return len(self._accounts)

    def load_all(self) -> List[PersonalAccount]:
        """Load accounts from the in-memory storage"""
        return self._accounts.copy()
