import pytest

from app.api import app, registry


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clear_registry():
    registry.accounts.clear()
    yield
    registry.accounts.clear()


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
    assert response3.json["name"] == "Charlie"

    # Delete one account
    delete_response = client.delete(f"/api/accounts/{pesel2}")
    assert delete_response.status_code == 200

    # Verify count decreased
    count_response = client.get("/api/accounts/count")
    assert count_response.json["count"] == 2

    # Verify deleted account returns 404
    response = client.get(f"/api/accounts/{pesel2}")
    assert response.status_code == 404

    # Verify other accounts still exist
    response1 = client.get(f"/api/accounts/{pesel1}")
    assert response1.status_code == 200

    response3 = client.get(f"/api/accounts/{pesel3}")
    assert response3.status_code == 200
