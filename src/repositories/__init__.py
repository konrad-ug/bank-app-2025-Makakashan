from abc import ABC, abstractmethod
from typing import List, Optional

from src.account import PersonalAccount


class AccountRepositoryInterface(ABC):
    """Abstract interface for account storage"""

    @abstractmethod
    def add(self, account: PersonalAccount) -> None:  # pragma: no cover
        """Add an account to the repository"""
        pass

    @abstractmethod
    def find_by_pesel(
        self, pesel: str
    ) -> Optional[PersonalAccount]:  # pragma: no cover
        """Find an account by PESEL"""
        pass

    @abstractmethod
    def get_all(self) -> List[PersonalAccount]:  # pragma: no cover
        """Get all accounts"""
        pass

    @abstractmethod
    def count(self) -> int:  # pragma: no cover
        """Get the total number of accounts"""
        pass

    @abstractmethod
    def update(
        self,
        pesel: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Optional[PersonalAccount]:  # pragma: no cover
        """Update an account"""
        pass

    @abstractmethod
    def delete(self, pesel: str) -> bool:  # pragma: no cover
        """Delete an account by PESEL"""
        pass

    @abstractmethod
    def clear(self) -> None:  # pragma: no cover
        """Clear all accounts from the repository"""
        pass

    @abstractmethod
    def save_all(self, accounts: List[PersonalAccount]) -> int:  # pragma: no cover
        """Persist all provided accounts, replacing existing data and return saved count"""
        pass

    @abstractmethod
    def load_all(self) -> List[PersonalAccount]:  # pragma: no cover
        """Load accounts from persistent storage"""
        pass
