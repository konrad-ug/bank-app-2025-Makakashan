import os
from typing import Any, List, Optional

from src.account import PersonalAccount
from src.repositories import AccountRepositoryInterface

try:
    from pymongo import MongoClient as PyMongoClient
except Exception:  # pragma: no cover - optional dependency shim
    PyMongoClient = None  # type: ignore

try:
    from mongomock import MongoClient as MockMongoClient
except Exception:  # pragma: no cover - optional dependency shim
    MockMongoClient = None  # type: ignore


class MongoAccountsRepository(AccountRepositoryInterface):
    """MongoDB implementation of account repository with bulk persistence helpers."""

    def __init__(
        self,
        connection_string: Optional[str] = None,
        database_name: str = "bank_app",
        collection_name: str = "accounts",
        client: Optional[Any] = None,
    ):
        """
        Initialize MongoDB repository.

        Args:
            connection_string: MongoDB connection string or special mongomock:// URI.
            database_name: Name of the database to use.
            collection_name: Name of the collection to use.
            client: Optional pre-configured Mongo client instance (real or mock).
        """
        if client is not None:
            self.client = client
        else:
            conn = connection_string or os.getenv(
                "MONGO_URI", "mongodb://localhost:27017/"
            )
            if conn.startswith("mongomock://") or conn == "mock":
                if MockMongoClient is None:  # pragma: no cover
                    raise RuntimeError(
                        "mongomock is required for mongomock:// connections"
                    )
                self.client = MockMongoClient()
            else:
                if PyMongoClient is None:  # pragma: no cover
                    raise RuntimeError(
                        "pymongo must be installed to use MongoAccountRepository"
                    )
                self.client = PyMongoClient(conn)

        self.db = self.client[database_name]
        self.collection = self.db[collection_name]
        # Ensure PESEL uniqueness for safety; mongomock supports create_index as well.
        self.collection.create_index("pesel", unique=True)

    def _account_to_dict(self, account: PersonalAccount) -> dict:
        """Convert PersonalAccount to dictionary for MongoDB storage."""
        return {
            "first_name": account.first_name,
            "last_name": account.last_name,
            "balance": account.balance,
            "pesel": account.pesel,
            "promo_code": account.promo_code,
            "historia": account.historia,
        }

    def _dict_to_account(self, doc: dict) -> PersonalAccount:
        """Convert MongoDB document to PersonalAccount without promo bonus side-effects."""
        account = PersonalAccount(
            first_name=doc["first_name"],
            last_name=doc["last_name"],
            balance=0.0,
            pesel=doc["pesel"],
            promo_code=None,
        )
        account.balance = doc["balance"]
        account.historia = doc.get("historia", [])
        account.promo_code = doc.get("promo_code")
        return account

    def add(self, account: PersonalAccount) -> None:
        """Add an account to the repository."""
        self.collection.insert_one(self._account_to_dict(account))

    def find_by_pesel(self, pesel: str) -> Optional[PersonalAccount]:
        """Find an account by PESEL."""
        doc = self.collection.find_one({"pesel": pesel})
        return None if doc is None else self._dict_to_account(doc)

    def get_all(self) -> List[PersonalAccount]:
        """Get all accounts."""
        return [self._dict_to_account(doc) for doc in self.collection.find()]

    def count(self) -> int:
        """Get the total number of accounts."""
        return self.collection.count_documents({})

    def update(
        self,
        pesel: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Optional[PersonalAccount]:
        """Update an account's names."""
        update_fields = {}
        if first_name is not None:
            update_fields["first_name"] = first_name
        if last_name is not None:
            update_fields["last_name"] = last_name

        if not update_fields:
            return self.find_by_pesel(pesel)

        result = self.collection.update_one({"pesel": pesel}, {"$set": update_fields})
        if result.matched_count == 0:
            return None
        return self.find_by_pesel(pesel)

    def delete(self, pesel: str) -> bool:
        """Delete an account by PESEL."""
        result = self.collection.delete_one({"pesel": pesel})
        return result.deleted_count > 0

    def clear(self) -> None:
        """Clear all accounts from the repository."""
        self.collection.delete_many({})

    def save_all(self, accounts: List[PersonalAccount]) -> int:
        """Persist all provided accounts, replacing existing data, and return count saved."""
        self.collection.delete_many({})
        if not accounts:
            return 0
        documents = [self._account_to_dict(account) for account in accounts]
        self.collection.insert_many(documents)
        return len(documents)

    def load_all(self) -> List[PersonalAccount]:
        """Load every account currently stored in the collection."""
        return self.get_all()

    def close(self) -> None:
        """Close the MongoDB connection if the client exposes close()."""
        close_fn = getattr(self.client, "close", None)
        if callable(close_fn):
            close_fn()


# Backward compatibility alias for legacy imports
MongoAccountRepository = MongoAccountsRepository
