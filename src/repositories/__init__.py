from abc import ABC, abstractmethod
from typing import List, Optional

from src.account import PersonalAccount


class AccountRepositoryInterface(ABC):
    """Abstract interface for account storage"""

    @abstractmethod
    def add(self, account: PersonalAccount) -> None:
        """Add an account to the repository"""
        pass

    @abstractmethod
    def find_by_pesel(self, pesel: str) -> Optional[PersonalAccount]:
        """Find an account by PESEL"""
        pass

    @abstractmethod
    def get_all(self) -> List[PersonalAccount]:
        """Get all accounts"""
        pass

    @abstractmethod
    def count(self) -> int:
        """Get the total number of accounts"""
        pass

    @abstractmethod
    def update(
        self,
        pesel: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Optional[PersonalAccount]:
        """Update an account"""
        pass

    @abstractmethod
    def delete(self, pesel: str) -> bool:
        """Delete an account by PESEL"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all accounts from the repository"""
        pass

    @abstractmethod
    def save_all(self, accounts: List[PersonalAccount]) -> int:
        """Persist all provided accounts, replacing existing data and return saved count"""
        pass

    @abstractmethod
    def load_all(self) -> List[PersonalAccount]:
        """Load accounts from persistent storage"""
        pass
