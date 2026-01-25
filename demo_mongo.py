#!/usr/bin/env python3
"""
Demo script to demonstrate MongoDB integration with AccountRegistry.
This script shows how the repository pattern works with both in-memory
and MongoDB storage backends.
"""

from mongomock import MongoClient

from src.account import PersonalAccount
from src.registry import AccountRegistry
from src.repositories.memory_repository import InMemoryAccountRepository
from src.repositories.mongo_repository import MongoAccountRepository


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_in_memory_repository():
    """Demonstrate AccountRegistry with in-memory repository"""
    print_section("DEMO 1: In-Memory Repository")

    # Create registry with default (in-memory) repository
    registry = AccountRegistry()

    print("\n✓ Created AccountRegistry with InMemoryAccountRepository")
    print(f"  Initial account count: {registry.get_account_count()}")

    # Add accounts
    print("\n→ Adding accounts...")
    account1 = PersonalAccount("Jan", "Kowalski", 1000.0, "80010112345")
    account2 = PersonalAccount("Anna", "Nowak", 2000.0, "90020254321")
    account3 = PersonalAccount("Piotr", "Wiśniewski", 1500.0, "85050598765")

    registry.add_account(account1)
    registry.add_account(account2)
    registry.add_account(account3)

    print(f"  Added 3 accounts")
    print(f"  Current account count: {registry.get_account_count()}")

    # Perform transactions
    print("\n→ Performing transactions on Jan's account...")
    jan = registry.find_account_by_pesel("80010112345")
    jan.incoming_transfer(500)
    jan.outgoing_transfer(200)
    print(f"  Jan's balance: {jan.balance}")
    print(f"  Jan's history: {jan.historia}")

    # Update account
    print("\n→ Updating Anna's name...")
    updated = registry.update_account("90020254321", first_name="Ania")
    print(f"  Updated name: {updated.first_name} {updated.last_name}")

    # Delete account
    print("\n→ Deleting Piotr's account...")
    deleted = registry.delete_account("85050598765")
    print(f"  Deletion successful: {deleted}")
    print(f"  Current account count: {registry.get_account_count()}")

    # List all accounts
    print("\n→ All remaining accounts:")
    for acc in registry.get_all_accounts():
        print(f"  - {acc.first_name} {acc.last_name} (PESEL: {acc.pesel}, Balance: {acc.balance})")


def demo_mongo_repository():
    """Demonstrate AccountRegistry with MongoDB repository"""
    print_section("DEMO 2: MongoDB Repository (using mongomock)")

    # Create MongoDB repository with mongomock
    print("\n✓ Creating MongoDB repository with mongomock...")
    client = MongoClient()
    mongo_repo = MongoAccountRepository.__new__(MongoAccountRepository)
    mongo_repo.client = client
    mongo_repo.db = client["demo_bank_app"]
    mongo_repo.collection = mongo_repo.db["accounts"]
    mongo_repo.collection.create_index("pesel", unique=True)

    # Create registry with MongoDB repository
    registry = AccountRegistry(repository=mongo_repo)
    print("  ✓ Created AccountRegistry with MongoAccountRepository")
    print(f"  Initial account count: {registry.get_account_count()}")

    # Add accounts
    print("\n→ Adding accounts to MongoDB...")
    account1 = PersonalAccount("Marek", "Kowalewski", 3000.0, "70010112345")
    account2 = PersonalAccount("Ewa", "Nowacka", 4000.0, "75020254321")

    registry.add_account(account1)
    registry.add_account(account2)

    print(f"  Added 2 accounts to MongoDB")
    print(f"  Current account count: {registry.get_account_count()}")

    # Perform transactions
    print("\n→ Performing transactions on Marek's account...")
    marek = registry.find_account_by_pesel("70010112345")
    marek.incoming_transfer(1000)
    marek.outgoing_transfer(500)
    print(f"  Marek's balance: {marek.balance}")
    print(f"  Marek's history: {marek.historia}")

    # Update account in MongoDB
    print("\n→ Updating account in MongoDB...")
    registry.update_account("70010112345", first_name="Marek", last_name="Kowalski")

    # Retrieve from MongoDB to verify persistence
    print("\n→ Retrieving account from MongoDB to verify persistence...")
    retrieved = registry.find_account_by_pesel("70010112345")
    print(f"  Retrieved: {retrieved.first_name} {retrieved.last_name}")
    print(f"  Balance: {retrieved.balance}")
    print(f"  History: {retrieved.historia}")

    # Test duplicate PESEL protection
    print("\n→ Testing duplicate PESEL protection...")
    try:
        duplicate = PersonalAccount("Test", "User", 5000.0, "70010112345")
        registry.add_account(duplicate)
        print("  ✗ ERROR: Duplicate was allowed!")
    except Exception as e:
        print(f"  ✓ Duplicate prevented: {type(e).__name__}")

    # List all accounts
    print("\n→ All accounts in MongoDB:")
    for acc in registry.get_all_accounts():
        print(f"  - {acc.first_name} {acc.last_name} (PESEL: {acc.pesel}, Balance: {acc.balance})")

    # Cleanup
    print("\n→ Cleaning up MongoDB...")
    registry.clear_all_accounts()
    print(f"  Account count after cleanup: {registry.get_account_count()}")
    mongo_repo.close()
    print("  ✓ MongoDB connection closed")


def demo_repository_comparison():
    """Demonstrate the flexibility of the repository pattern"""
    print_section("DEMO 3: Repository Pattern Flexibility")

    print("\n✓ The Repository Pattern allows us to:")
    print("  1. Switch storage backends without changing business logic")
    print("  2. Test with in-memory storage for speed")
    print("  3. Use MongoDB for production persistence")
    print("  4. Mock repositories for unit testing")

    print("\n→ Example: Same registry code, different storage")

    # In-memory version
    print("\n  [In-Memory]")
    memory_registry = AccountRegistry()  # Default: InMemoryAccountRepository
    memory_registry.add_account(PersonalAccount("Test", "User", 100.0, "12345678901"))
    print(f"    Count: {memory_registry.get_account_count()}")
    print(f"    Type: {type(memory_registry._repository).__name__}")

    # MongoDB version
    print("\n  [MongoDB]")
    client = MongoClient()
    mongo_repo = MongoAccountRepository.__new__(MongoAccountRepository)
    mongo_repo.client = client
    mongo_repo.db = client["demo_bank_app"]
    mongo_repo.collection = mongo_repo.db["accounts"]
    mongo_repo.collection.create_index("pesel", unique=True)

    mongo_registry = AccountRegistry(repository=mongo_repo)
    mongo_registry.add_account(PersonalAccount("Test", "User", 100.0, "98765432109"))
    print(f"    Count: {mongo_registry.get_account_count()}")
    print(f"    Type: {type(mongo_registry._repository).__name__}")

    # Cleanup
    mongo_registry.clear_all_accounts()
    mongo_repo.close()

    print("\n✓ Both registries use the same interface!")


def demo_history_persistence():
    """Demonstrate that transaction history persists in MongoDB"""
    print_section("DEMO 4: Transaction History Persistence")

    # Setup MongoDB
    client = MongoClient()
    mongo_repo = MongoAccountRepository.__new__(MongoAccountRepository)
    mongo_repo.client = client
    mongo_repo.db = client["demo_bank_app"]
    mongo_repo.collection = mongo_repo.db["accounts"]
    mongo_repo.collection.create_index("pesel", unique=True)

    registry = AccountRegistry(repository=mongo_repo)

    print("\n→ Creating account with transactions...")
    account = PersonalAccount("Barbara", "Kowalska", 5000.0, "60010112345", promo_code="PROM_123")

    # Check if promo code bonus was applied
    print(f"  Initial balance (with promo bonus): {account.balance}")
    print(f"  Initial history: {account.historia}")

    # Perform transactions
    account.incoming_transfer(1000)
    account.outgoing_transfer(500)
    account.incoming_transfer(250)

    print(f"  After transactions - Balance: {account.balance}")
    print(f"  After transactions - History: {account.historia}")

    # Save to MongoDB
    print("\n→ Saving to MongoDB...")
    registry.add_account(account)

    # Retrieve from MongoDB
    print("\n→ Retrieving from MongoDB...")
    retrieved = registry.find_account_by_pesel("60010112345")
    print(f"  Retrieved balance: {retrieved.balance}")
    print(f"  Retrieved history: {retrieved.historia}")
    print(f"  Retrieved promo_code: {retrieved.promo_code}")

    # Verify data integrity
    if retrieved.balance == account.balance and retrieved.historia == account.historia:
        print("\n  ✓ SUCCESS: All data persisted correctly!")
    else:
        print("\n  ✗ ERROR: Data mismatch!")

    # Cleanup
    registry.clear_all_accounts()
    mongo_repo.close()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Bank Application - MongoDB Integration Demo".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    # Run all demos
    demo_in_memory_repository()
    demo_mongo_repository()
    demo_repository_comparison()
    demo_history_persistence()

    # Final summary
    print_section("Summary")
    print("\n✓ Demonstrated:")
    print("  1. In-memory repository for fast, temporary storage")
    print("  2. MongoDB repository for persistent storage")
    print("  3. Repository pattern flexibility")
    print("  4. Transaction history persistence")
    print("  5. Duplicate PESEL prevention")
    print("  6. CRUD operations (Create, Read, Update, Delete)")
    print("\n✓ Key Benefits:")
    print("  • Clean separation of concerns")
    print("  • Easy to test with mocks")
    print("  • Flexible storage backend selection")
    print("  • Production-ready MongoDB integration")

    print("\n" + "=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)
    print("\nFor more details, run the test suite:")
    print("  python -m pytest tests/unit/test_registry.py -v")
    print("  python -m pytest tests/unit/test_mongo_repository.py -v")
    print()
