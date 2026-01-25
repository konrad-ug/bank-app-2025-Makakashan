import os

import pytest

try:
    from pymongo import MongoClient as PyMongoClient
except Exception:  # pragma: no cover - optional dependency
    PyMongoClient = None

from mongomock import MongoClient as MockMongoClient

from app.api import app, registry
from src.repositories.mongo_repository import MongoAccountsRepository


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clear_registry():
    registry.clear_all_accounts()
    yield
    registry.clear_all_accounts()


@pytest.fixture
def mongo_repository_factory():
    mongo_uri = os.getenv("API_TEST_MONGO_URI")
    db_name = os.getenv("API_TEST_MONGO_DB_NAME", "bank_app_api_tests")
    collection_name = os.getenv("API_TEST_MONGO_COLLECTION", "accounts_api_tests")

    use_real_mongo = bool(mongo_uri)
    if use_real_mongo:
        if PyMongoClient is None:
            pytest.skip(
                "pymongo is required to run API tests against a real Mongo instance"
            )
        client = PyMongoClient(mongo_uri)
    else:
        client = MockMongoClient()

    repo_kwargs = {
        "client": client,
        "database_name": db_name,
        "collection_name": collection_name,
    }
    repo = MongoAccountsRepository(**repo_kwargs)
    repo.clear()

    def factory(**_kwargs):
        return MongoAccountsRepository(**repo_kwargs)

    if not use_real_mongo:
        app.config["ACCOUNTS_REPOSITORY_FACTORY"] = factory
    app.config["PERSISTENCE_CONFIG"] = {
        "connection_string": mongo_uri if use_real_mongo else "mock",
        "database_name": db_name,
        "collection_name": collection_name,
    }

    try:
        yield repo
    finally:
        repo.clear()
        close_fn = getattr(client, "close", None)
        if callable(close_fn):
            close_fn()
        app.config.pop("ACCOUNTS_REPOSITORY_FACTORY", None)
        app.config.pop("PERSISTENCE_CONFIG", None)


def test_create_account(client):
    response = client.post(
        "/api/accounts",
        json={"name": "James", "surname": "Hetfield", "pesel": "89092909825"},
    )
    assert response.status_code == 201
    assert response.json == {"message": "Account created"}


def test_get_all_accounts_empty(client):
    response = client.get("/api/accounts")
    assert response.status_code == 200
    assert response.json == []


def test_get_all_accounts(client):
    client.post(
        "/api/accounts",
        json={"name": "James", "surname": "Hetfield", "pesel": "11111111111"},
    )
    client.post(
        "/api/accounts",
        json={"name": "Kirk", "surname": "Hammett", "pesel": "22222222222"},
    )

    response = client.get("/api/accounts")
    assert response.status_code == 200
    assert len(response.json) == 2


def test_get_account_count(client):
    response = client.get("/api/accounts/count")
    assert response.status_code == 200
    assert response.json == {"count": 0}

    client.post(
        "/api/accounts",
        json={"name": "Test", "surname": "User", "pesel": "12345678901"},
    )

    response = client.get("/api/accounts/count")
    assert response.status_code == 200
    assert response.json == {"count": 1}


def test_get_account_by_pesel(client):
    pesel = "89092909825"
    client.post(
        "/api/accounts",
        json={"name": "James", "surname": "Hetfield", "pesel": pesel},
    )

    response = client.get(f"/api/accounts/{pesel}")
    assert response.status_code == 200
    assert response.json["name"] == "James"
    assert response.json["surname"] == "Hetfield"
    assert response.json["pesel"] == pesel


def test_get_account_by_pesel_not_found(client):
    response = client.get("/api/accounts/99999999999")
    assert response.status_code == 404


def test_update_account(client):
    pesel = "89092909825"
    client.post(
        "/api/accounts",
        json={"name": "James", "surname": "Hetfield", "pesel": pesel},
    )

    response = client.put(
        f"/api/accounts/{pesel}",
        json={"name": "Lars", "surname": "Ulrich"},
    )
    assert response.status_code == 200
    assert response.json["name"] == "Lars"
    assert response.json["surname"] == "Ulrich"
    assert response.json["pesel"] == pesel

    # Verify the update persisted
    response = client.get(f"/api/accounts/{pesel}")
    assert response.status_code == 200
    assert response.json["name"] == "Lars"
    assert response.json["surname"] == "Ulrich"


def test_update_account_not_found(client):
    response = client.put(
        "/api/accounts/99999999999",
        json={"name": "Test", "surname": "User"},
    )
    assert response.status_code == 404


def test_delete_account(client):
    pesel = "89092909825"
    client.post(
        "/api/accounts",
        json={"name": "James", "surname": "Hetfield", "pesel": pesel},
    )

    response = client.delete(f"/api/accounts/{pesel}")
    assert response.status_code == 200
    assert response.json == {"message": "Account deleted"}

    # Verify the account is deleted
    response = client.get(f"/api/accounts/{pesel}")
    assert response.status_code == 404


def test_delete_account_not_found(client):
    response = client.delete("/api/accounts/99999999999")
    assert response.status_code == 404


def test_full_crud_integration(client):
    """Comprehensive integration test for full CRUD cycle"""
    pesel = "85123112345"

    # CREATE - Create a new account
    create_response = client.post(
        "/api/accounts",
        json={"name": "Robert", "surname": "Trujillo", "pesel": pesel},
    )
    assert create_response.status_code == 201
    assert create_response.json == {"message": "Account created"}

    # READ - Verify account exists
    get_response = client.get(f"/api/accounts/{pesel}")
    assert get_response.status_code == 200
    assert get_response.json["name"] == "Robert"
    assert get_response.json["surname"] == "Trujillo"
    assert get_response.json["pesel"] == pesel
    assert get_response.json["balance"] == 0.0

    # READ - Verify account count increased
    count_response = client.get("/api/accounts/count")
    assert count_response.status_code == 200
    assert count_response.json["count"] == 1

    # UPDATE - Update account details
    update_response = client.put(
        f"/api/accounts/{pesel}",
        json={"name": "Jason", "surname": "Newsted"},
    )
    assert update_response.status_code == 200
    assert update_response.json["name"] == "Jason"
    assert update_response.json["surname"] == "Newsted"
    assert update_response.json["pesel"] == pesel

    # READ - Verify update persisted
    verify_update = client.get(f"/api/accounts/{pesel}")
    assert verify_update.status_code == 200
    assert verify_update.json["name"] == "Jason"
    assert verify_update.json["surname"] == "Newsted"

    # DELETE - Delete the account
    delete_response = client.delete(f"/api/accounts/{pesel}")
    assert delete_response.status_code == 200
    assert delete_response.json == {"message": "Account deleted"}

    # READ - Verify account is gone (404)
    verify_delete = client.get(f"/api/accounts/{pesel}")
    assert verify_delete.status_code == 404

    # READ - Verify account count decreased
    final_count = client.get("/api/accounts/count")
    assert final_count.status_code == 200
    assert final_count.json["count"] == 0


def test_update_account_partial_name_only(client):
    """Test updating only the first name"""
    pesel = "88050512345"
    client.post(
        "/api/accounts",
        json={"name": "John", "surname": "Doe", "pesel": pesel},
    )

    response = client.put(
        f"/api/accounts/{pesel}",
        json={"name": "Jane"},
    )
    assert response.status_code == 200
    assert response.json["name"] == "Jane"
    assert response.json["surname"] == "Doe"  # Surname unchanged


def test_update_account_partial_surname_only(client):
    """Test updating only the last name"""
    pesel = "90010112345"
    client.post(
        "/api/accounts",
        json={"name": "John", "surname": "Doe", "pesel": pesel},
    )

    response = client.put(
        f"/api/accounts/{pesel}",
        json={"surname": "Smith"},
    )
    assert response.status_code == 200
    assert response.json["name"] == "John"  # Name unchanged
    assert response.json["surname"] == "Smith"


def test_multiple_accounts_operations(client):
    """Test operations with multiple accounts"""
    pesel1 = "85010112345"
    pesel2 = "86020212345"
    pesel3 = "87030312345"

    # Create multiple accounts
    client.post(
        "/api/accounts",
        json={"name": "Alice", "surname": "Smith", "pesel": pesel1},
    )
    client.post(
        "/api/accounts",
        json={"name": "Bob", "surname": "Jones", "pesel": pesel2},
    )
    client.post(
        "/api/accounts",
        json={"name": "Charlie", "surname": "Brown", "pesel": pesel3},
    )

    # Verify count
    count_response = client.get("/api/accounts/count")
    assert count_response.json["count"] == 3

    # Verify all accounts exist
    response1 = client.get(f"/api/accounts/{pesel1}")
    assert response1.status_code == 200
    assert response1.json["name"] == "Alice"

    response2 = client.get(f"/api/accounts/{pesel2}")
    assert response2.status_code == 200
    assert response2.json["name"] == "Bob"

    response3 = client.get(f"/api/accounts/{pesel3}")
    assert response3.status_code == 200


# ============================================================================
# Feature 16: Unique PESEL Tests
# ============================================================================


def test_create_account_with_duplicate_pesel_returns_409(client):
    """Test that creating account with duplicate PESEL returns 409"""
    pesel = "89092909825"

    # Create first account
    response1 = client.post(
        "/api/accounts",
        json={"name": "James", "surname": "Hetfield", "pesel": pesel},
    )
    assert response1.status_code == 201

    # Try to create second account with same PESEL
    response2 = client.post(
        "/api/accounts",
        json={"name": "Lars", "surname": "Ulrich", "pesel": pesel},
    )
    assert response2.status_code == 409
    assert "error" in response2.json
    assert pesel in response2.json["error"]


def test_duplicate_pesel_does_not_create_account(client):
    """Test that duplicate PESEL attempt doesn't create a second account"""
    pesel = "85010112345"

    # Create first account
    client.post(
        "/api/accounts",
        json={"name": "Alice", "surname": "Smith", "pesel": pesel},
    )

    # Try to create second account with same PESEL
    client.post(
        "/api/accounts",
        json={"name": "Bob", "surname": "Jones", "pesel": pesel},
    )

    # Verify only one account exists
    count_response = client.get("/api/accounts/count")
    assert count_response.json["count"] == 1

    # Verify the first account is still there
    get_response = client.get(f"/api/accounts/{pesel}")
    assert get_response.json["name"] == "Alice"
    assert get_response.json["surname"] == "Smith"


def test_different_pesels_can_be_created(client):
    """Test that accounts with different PESELs can be created successfully"""
    response1 = client.post(
        "/api/accounts",
        json={"name": "Alice", "surname": "Smith", "pesel": "85010112345"},
    )
    assert response1.status_code == 201

    response2 = client.post(
        "/api/accounts",
        json={"name": "Bob", "surname": "Jones", "pesel": "86020212345"},
    )
    assert response2.status_code == 201

    response3 = client.post(
        "/api/accounts",
        json={"name": "Charlie", "surname": "Brown", "pesel": "87030312345"},
    )
    assert response3.status_code == 201

    count_response = client.get("/api/accounts/count")
    assert count_response.json["count"] == 3


def test_delete_and_recreate_with_same_pesel_succeeds(client):
    """Test that after deleting, same PESEL can be used again"""
    pesel = "89092909825"

    # Create account
    response1 = client.post(
        "/api/accounts",
        json={"name": "James", "surname": "Hetfield", "pesel": pesel},
    )
    assert response1.status_code == 201

    # Delete account
    delete_response = client.delete(f"/api/accounts/{pesel}")
    assert delete_response.status_code == 200

    # Create new account with same PESEL
    response2 = client.post(
        "/api/accounts",
        json={"name": "Lars", "surname": "Ulrich", "pesel": pesel},
    )
    assert response2.status_code == 201

    # Verify new account details
    get_response = client.get(f"/api/accounts/{pesel}")
    assert get_response.json["name"] == "Lars"
    assert get_response.json["surname"] == "Ulrich"


def test_save_accounts_to_persistence(client, mongo_repository_factory):
    client.post(
        "/api/accounts",
        json={"name": "Alice", "surname": "Smith", "pesel": "85010112345"},
    )
    client.post(
        "/api/accounts",
        json={"name": "Bob", "surname": "Jones", "pesel": "86020212345"},
    )

    response = client.post("/api/accounts/save")
    assert response.status_code == 200
    assert response.json["message"] == "Accounts saved to MongoDB"
    assert response.json["count"] == 2
    assert mongo_repository_factory.count() == 2


def test_load_accounts_from_persistence_replaces_registry(
    client, mongo_repository_factory
):
    pesel1 = "85010112345"
    pesel2 = "86020212345"

    client.post(
        "/api/accounts",
        json={"name": "Alice", "surname": "Smith", "pesel": pesel1},
    )
    client.post(
        "/api/accounts",
        json={"name": "Bob", "surname": "Jones", "pesel": pesel2},
    )
    client.post("/api/accounts/save")

    registry.clear_all_accounts()
    load_response = client.post("/api/accounts/load")
    assert load_response.status_code == 200
    assert load_response.json["message"] == "Accounts loaded from MongoDB"
    assert load_response.json["count"] == 2

    accounts_response = client.get("/api/accounts")
    assert accounts_response.status_code == 200
    assert len(accounts_response.json) == 2
    assert {pesel1, pesel2} == {acc["pesel"] for acc in accounts_response.json}


# ============================================================================
# Feature 17: Transfer API Tests
# ============================================================================


@pytest.fixture
def account_with_balance(client):
    """Fixture that creates an account with initial balance"""
    pesel = "85123112345"
    client.post(
        "/api/accounts",
        json={"name": "Robert", "surname": "Trujillo", "pesel": pesel},
    )

    # Add some balance through incoming transfer
    client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 1000, "type": "incoming"},
    )

    return pesel


def test_incoming_transfer_success(client, account_with_balance):
    """Test successful incoming transfer"""
    pesel = account_with_balance

    response = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 500, "type": "incoming"},
    )

    assert response.status_code == 200
    assert response.json == {"message": "Zlecenie przyjęto do realizacji"}

    # Verify balance increased
    account = client.get(f"/api/accounts/{pesel}")
    assert account.json["balance"] == 1500.0  # 1000 + 500


def test_outgoing_transfer_success(client, account_with_balance):
    """Test successful outgoing transfer"""
    pesel = account_with_balance

    response = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 300, "type": "outgoing"},
    )

    assert response.status_code == 200
    assert response.json == {"message": "Zlecenie przyjęto do realizacji"}

    # Verify balance decreased
    account = client.get(f"/api/accounts/{pesel}")
    assert account.json["balance"] == 700.0  # 1000 - 300


def test_express_transfer_success(client, account_with_balance):
    """Test successful express transfer"""
    pesel = account_with_balance

    response = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 300, "type": "express"},
    )

    assert response.status_code == 200
    assert response.json == {"message": "Zlecenie przyjęto do realizacji"}

    # Verify balance decreased (amount + 1.0 fee for PersonalAccount)
    account = client.get(f"/api/accounts/{pesel}")
    assert account.json["balance"] == 699.0  # 1000 - 300 - 1


def test_transfer_account_not_found_returns_404(client):
    """Test transfer to non-existent account returns 404"""
    response = client.post(
        "/api/accounts/99999999999/transfer",
        json={"amount": 500, "type": "incoming"},
    )

    assert response.status_code == 404
    assert "error" in response.json
    assert "not found" in response.json["error"].lower()


def test_outgoing_transfer_insufficient_funds_returns_422(client):
    """Test outgoing transfer with insufficient funds returns 422"""
    pesel = "88050512345"
    client.post(
        "/api/accounts",
        json={"name": "Jane", "surname": "Doe", "pesel": pesel},
    )

    # Add 100 to balance
    client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 100, "type": "incoming"},
    )

    # Try to transfer more than balance
    response = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 500, "type": "outgoing"},
    )

    assert response.status_code == 422
    assert "error" in response.json


def test_express_transfer_insufficient_funds_returns_422(client):
    """Test express transfer with insufficient funds returns 422"""
    pesel = "90010112345"
    client.post(
        "/api/accounts",
        json={"name": "John", "surname": "Smith", "pesel": pesel},
    )

    # Add 50 to balance
    client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 50, "type": "incoming"},
    )

    # Try to transfer more than balance (100 > 50, so should fail)
    response = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 100, "type": "express"},
    )

    assert response.status_code == 422
    assert "error" in response.json


def test_invalid_transfer_type_returns_400(client, account_with_balance):
    """Test that invalid transfer type returns 400"""
    pesel = account_with_balance

    response = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 500, "type": "invalid_type"},
    )

    assert response.status_code == 400
    assert "error" in response.json
    assert "Invalid transfer type" in response.json["error"]


def test_transfer_missing_amount_returns_400(client, account_with_balance):
    """Test that missing amount field returns 400"""
    pesel = account_with_balance

    response = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"type": "incoming"},
    )

    assert response.status_code == 400
    assert "error" in response.json


def test_transfer_missing_type_returns_400(client, account_with_balance):
    """Test that missing type field returns 400"""
    pesel = account_with_balance

    response = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 500},
    )

    assert response.status_code == 400
    assert "error" in response.json


def test_transfer_negative_amount_returns_400(client, account_with_balance):
    """Test that negative amount returns 400"""
    pesel = account_with_balance

    response = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": -500, "type": "incoming"},
    )

    assert response.status_code == 400
    assert "error" in response.json


def test_transfer_zero_amount_returns_400(client, account_with_balance):
    """Test that zero amount returns 400"""
    pesel = account_with_balance

    response = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 0, "type": "incoming"},
    )

    assert response.status_code == 400
    assert "error" in response.json


def test_multiple_transfers_on_same_account(client):
    """Test multiple transfers on the same account"""
    pesel = "87654321098"
    client.post(
        "/api/accounts",
        json={"name": "Test", "surname": "User", "pesel": pesel},
    )

    # Incoming transfer
    response1 = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 1000, "type": "incoming"},
    )
    assert response1.status_code == 200

    # Another incoming transfer
    response2 = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 500, "type": "incoming"},
    )
    assert response2.status_code == 200

    # Outgoing transfer
    response3 = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 300, "type": "outgoing"},
    )
    assert response3.status_code == 200

    # Express transfer
    response4 = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 200, "type": "express"},
    )
    assert response4.status_code == 200

    # Verify final balance: 1000 + 500 - 300 - 200 - 1 (fee) = 999
    account = client.get(f"/api/accounts/{pesel}")
    assert account.json["balance"] == 999.0


def test_transfer_with_float_amount(client, account_with_balance):
    """Test transfer with decimal amount"""
    pesel = account_with_balance

    response = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 123.45, "type": "incoming"},
    )

    assert response.status_code == 200

    # Verify balance increased correctly
    account = client.get(f"/api/accounts/{pesel}")
    assert account.json["balance"] == 1123.45  # 1000 + 123.45


def test_outgoing_transfer_exact_balance(client):
    """Test outgoing transfer for exact balance amount"""
    pesel = "86420197531"
    client.post(
        "/api/accounts",
        json={"name": "Test", "surname": "User", "pesel": pesel},
    )

    # Add 500 to balance
    client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 500, "type": "incoming"},
    )

    # Transfer exact balance
    response = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 500, "type": "outgoing"},
    )

    assert response.status_code == 200

    # Verify balance is now 0
    account = client.get(f"/api/accounts/{pesel}")
    assert account.json["balance"] == 0.0


def test_transfer_case_sensitive_type(client, account_with_balance):
    """Test that transfer type is case-sensitive"""
    pesel = account_with_balance

    # Try with uppercase
    response = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": 100, "type": "INCOMING"},
    )

    assert response.status_code == 400
    assert "error" in response.json


def test_transfer_string_amount_returns_400(client, account_with_balance):
    """Test that string amount returns 400"""
    pesel = account_with_balance

    response = client.post(
        f"/api/accounts/{pesel}/transfer",
        json={"amount": "not_a_number", "type": "incoming"},
    )

    assert response.status_code == 400
    assert "error" in response.json
