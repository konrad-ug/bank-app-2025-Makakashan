import os
import sys
import unittest

# Add parent directory to path to import app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.api import app, registry


class TestAccountCRUD(unittest.TestCase):
    """Test suite for Account CRUD operations via API"""

    def setUp(self):
        """Set up test client and clear registry before each test"""
        app.config["TESTING"] = True
        self.client = app.test_client()
        # Clear registry before each test to ensure independence
        registry.clear_all_accounts()

    def tearDown(self):
        """Clean up after each test"""
        # Clear registry after each test
        registry.clear_all_accounts()

    # CREATE tests
    def test_create_account(self):
        """Test creating a new account"""
        response = self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": "89092909825"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"message": "Account created"})

    def test_create_multiple_accounts(self):
        """Test creating multiple accounts independently"""
        # Create first account
        response1 = self.client.post(
            "/api/accounts",
            json={"name": "Alice", "surname": "Smith", "pesel": "85010112345"},
        )
        self.assertEqual(response1.status_code, 201)

        # Create second account
        response2 = self.client.post(
            "/api/accounts",
            json={"name": "Bob", "surname": "Jones", "pesel": "86020212345"},
        )
        self.assertEqual(response2.status_code, 201)

        # Verify both exist
        count_response = self.client.get("/api/accounts/count")
        self.assertEqual(count_response.json["count"], 2)

    # READ tests
    def test_get_all_accounts_empty(self):
        """Test getting all accounts when registry is empty"""
        response = self.client.get("/api/accounts")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_get_all_accounts(self):
        """Test getting all accounts with data"""
        # Create test data
        self.client.post(
            "/api/accounts",
            json={"name": "John", "surname": "Doe", "pesel": "11111111111"},
        )
        self.client.post(
            "/api/accounts",
            json={"name": "Jane", "surname": "Smith", "pesel": "22222222222"},
        )

        # Get all accounts
        response = self.client.get("/api/accounts")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    def test_get_account_by_pesel(self):
        """Test getting specific account by PESEL"""
        pesel = "89092909825"
        # Create account
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )

        # Get account by PESEL
        response = self.client.get(f"/api/accounts/{pesel}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "James")
        self.assertEqual(response.json["surname"], "Hetfield")
        self.assertEqual(response.json["pesel"], pesel)
        self.assertEqual(response.json["balance"], 0.0)

    def test_get_account_by_pesel_not_found(self):
        """Test 404 when account with given PESEL doesn't exist"""
        response = self.client.get("/api/accounts/99999999999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Account not found"})

    def test_get_account_count(self):
        """Test account count endpoint"""
        # Initially empty
        response = self.client.get("/api/accounts/count")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["count"], 0)

        # Add one account
        self.client.post(
            "/api/accounts",
            json={"name": "Test", "surname": "User", "pesel": "12345678901"},
        )

        # Count should be 1
        response = self.client.get("/api/accounts/count")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["count"], 1)

    # UPDATE tests
    def test_update_account(self):
        """Test updating account details"""
        pesel = "89092909825"
        # Create account
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )

        # Update account
        response = self.client.put(
            f"/api/accounts/{pesel}", json={"name": "Lars", "surname": "Ulrich"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Lars")
        self.assertEqual(response.json["surname"], "Ulrich")
        self.assertEqual(response.json["pesel"], pesel)

        # Verify update persisted
        verify_response = self.client.get(f"/api/accounts/{pesel}")
        self.assertEqual(verify_response.json["name"], "Lars")
        self.assertEqual(verify_response.json["surname"], "Ulrich")

    def test_update_account_not_found(self):
        """Test 404 when updating non-existent account"""
        response = self.client.put(
            "/api/accounts/99999999999", json={"name": "Test", "surname": "User"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Account not found"})

    def test_update_account_partial_name_only(self):
        """Test updating only first name"""
        pesel = "88050512345"
        # Create account
        self.client.post(
            "/api/accounts", json={"name": "John", "surname": "Doe", "pesel": pesel}
        )

        # Update only name
        response = self.client.put(f"/api/accounts/{pesel}", json={"name": "Jane"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Jane")
        self.assertEqual(response.json["surname"], "Doe")  # Unchanged

    def test_update_account_partial_surname_only(self):
        """Test updating only last name"""
        pesel = "90010112345"
        # Create account
        self.client.post(
            "/api/accounts", json={"name": "John", "surname": "Doe", "pesel": pesel}
        )

        # Update only surname
        response = self.client.put(f"/api/accounts/{pesel}", json={"surname": "Smith"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "John")  # Unchanged
        self.assertEqual(response.json["surname"], "Smith")

    # DELETE tests
    def test_delete_account(self):
        """Test deleting an account"""
        pesel = "89092909825"
        # Create account
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )

        # Delete account
        response = self.client.delete(f"/api/accounts/{pesel}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Account deleted"})

        # Verify account is deleted
        verify_response = self.client.get(f"/api/accounts/{pesel}")
        self.assertEqual(verify_response.status_code, 404)

    def test_delete_account_not_found(self):
        """Test 404 when deleting non-existent account"""
        response = self.client.delete("/api/accounts/99999999999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Account not found"})

    # Integration tests
    def test_full_crud_integration(self):
        """Comprehensive integration test for full CRUD cycle"""
        pesel = "85123112345"

        # CREATE
        create_response = self.client.post(
            "/api/accounts",
            json={"name": "Robert", "surname": "Trujillo", "pesel": pesel},
        )
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.json, {"message": "Account created"})

        # READ - verify account exists
        get_response = self.client.get(f"/api/accounts/{pesel}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json["name"], "Robert")
        self.assertEqual(get_response.json["surname"], "Trujillo")
        self.assertEqual(get_response.json["pesel"], pesel)
        self.assertEqual(get_response.json["balance"], 0.0)

        # READ - verify count
        count_response = self.client.get("/api/accounts/count")
        self.assertEqual(count_response.json["count"], 1)

        # UPDATE
        update_response = self.client.put(
            f"/api/accounts/{pesel}", json={"name": "Jason", "surname": "Newsted"}
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json["name"], "Jason")
        self.assertEqual(update_response.json["surname"], "Newsted")

        # READ - verify update persisted
        verify_update = self.client.get(f"/api/accounts/{pesel}")
        self.assertEqual(verify_update.json["name"], "Jason")
        self.assertEqual(verify_update.json["surname"], "Newsted")

        # DELETE
        delete_response = self.client.delete(f"/api/accounts/{pesel}")
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.json, {"message": "Account deleted"})

        # READ - verify deletion (404)
        verify_delete = self.client.get(f"/api/accounts/{pesel}")
        self.assertEqual(verify_delete.status_code, 404)

        # READ - verify count is 0
        final_count = self.client.get("/api/accounts/count")
        self.assertEqual(final_count.json["count"], 0)

    def test_multiple_accounts_operations(self):
        """Test operations with multiple accounts"""
        pesel1 = "85010112345"
        pesel2 = "86020212345"
        pesel3 = "87030312345"

        # Create multiple accounts
        self.client.post(
            "/api/accounts", json={"name": "Alice", "surname": "Smith", "pesel": pesel1}
        )
        self.client.post(
            "/api/accounts", json={"name": "Bob", "surname": "Jones", "pesel": pesel2}
        )
        self.client.post(
            "/api/accounts",
            json={"name": "Charlie", "surname": "Brown", "pesel": pesel3},
        )

        # Verify count
        count_response = self.client.get("/api/accounts/count")
        self.assertEqual(count_response.json["count"], 3)

        # Verify all accounts exist
        response1 = self.client.get(f"/api/accounts/{pesel1}")
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.json["name"], "Alice")

        response2 = self.client.get(f"/api/accounts/{pesel2}")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.json["name"], "Bob")

        response3 = self.client.get(f"/api/accounts/{pesel3}")
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(response3.json["name"], "Charlie")

        # Delete one account
        delete_response = self.client.delete(f"/api/accounts/{pesel2}")
        self.assertEqual(delete_response.status_code, 200)

        # Verify count decreased
        count_response = self.client.get("/api/accounts/count")
        self.assertEqual(count_response.json["count"], 2)

        # Verify deleted account returns 404
        response = self.client.get(f"/api/accounts/{pesel2}")
        self.assertEqual(response.status_code, 404)

        # Verify other accounts still exist
        response1 = self.client.get(f"/api/accounts/{pesel1}")
        self.assertEqual(response1.status_code, 200)

        response3 = self.client.get(f"/api/accounts/{pesel3}")
        self.assertEqual(response3.status_code, 200)

    # PESEL uniqueness tests (Feature 16)
    def test_create_account_with_duplicate_pesel_returns_409(self):
        """Test that creating account with duplicate PESEL returns 409 Conflict"""
        pesel = "89092909825"

        # Create first account
        response1 = self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )
        self.assertEqual(response1.status_code, 201)

        # Try to create second account with same PESEL
        response2 = self.client.post(
            "/api/accounts",
            json={"name": "Lars", "surname": "Ulrich", "pesel": pesel},
        )
        self.assertEqual(response2.status_code, 409)
        self.assertIn("error", response2.json)
        self.assertIn(pesel, response2.json["error"])
        self.assertIn("already exists", response2.json["error"])

    def test_duplicate_pesel_does_not_create_account(self):
        """Test that duplicate PESEL attempt doesn't add account to registry"""
        pesel = "88050512345"

        # Create first account
        self.client.post(
            "/api/accounts", json={"name": "John", "surname": "Doe", "pesel": pesel}
        )

        # Verify count is 1
        count_response = self.client.get("/api/accounts/count")
        self.assertEqual(count_response.json["count"], 1)

        # Try to create duplicate
        self.client.post(
            "/api/accounts", json={"name": "Jane", "surname": "Smith", "pesel": pesel}
        )

        # Count should still be 1
        count_response = self.client.get("/api/accounts/count")
        self.assertEqual(count_response.json["count"], 1)

        # Original account should be unchanged
        response = self.client.get(f"/api/accounts/{pesel}")
        self.assertEqual(response.json["name"], "John")
        self.assertEqual(response.json["surname"], "Doe")

    def test_different_pesels_can_create_multiple_accounts(self):
        """Test that different PESELs can create multiple accounts"""
        # Create accounts with different PESELs
        response1 = self.client.post(
            "/api/accounts",
            json={"name": "Alice", "surname": "Smith", "pesel": "85010112345"},
        )
        self.assertEqual(response1.status_code, 201)

        response2 = self.client.post(
            "/api/accounts",
            json={"name": "Bob", "surname": "Jones", "pesel": "86020212345"},
        )
        self.assertEqual(response2.status_code, 201)

        response3 = self.client.post(
            "/api/accounts",
            json={"name": "Charlie", "surname": "Brown", "pesel": "87030312345"},
        )
        self.assertEqual(response3.status_code, 201)

        # All should succeed
        count_response = self.client.get("/api/accounts/count")
        self.assertEqual(count_response.json["count"], 3)

    def test_delete_and_recreate_with_same_pesel_succeeds(self):
        """Test that after deleting account, same PESEL can be used again"""
        pesel = "89092909825"

        # Create account
        response1 = self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )
        self.assertEqual(response1.status_code, 201)

        # Delete account
        delete_response = self.client.delete(f"/api/accounts/{pesel}")
        self.assertEqual(delete_response.status_code, 200)

        # Create new account with same PESEL - should succeed
        response2 = self.client.post(
            "/api/accounts",
            json={"name": "Lars", "surname": "Ulrich", "pesel": pesel},
        )
        self.assertEqual(response2.status_code, 201)

        # Verify new account exists
        get_response = self.client.get(f"/api/accounts/{pesel}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json["name"], "Lars")
        self.assertEqual(get_response.json["surname"], "Ulrich")

    def test_multiple_duplicate_attempts_all_return_409(self):
        """Test that multiple attempts to create duplicate PESEL all return 409"""
        pesel = "90010112345"

        # Create first account
        response1 = self.client.post(
            "/api/accounts", json={"name": "First", "surname": "User", "pesel": pesel}
        )
        self.assertEqual(response1.status_code, 201)

        # Try to create duplicates multiple times
        for i in range(3):
            response = self.client.post(
                "/api/accounts",
                json={"name": f"User{i}", "surname": f"Duplicate{i}", "pesel": pesel},
            )
            self.assertEqual(response.status_code, 409)
            self.assertIn("error", response.json)

        # Only one account should exist
        count_response = self.client.get("/api/accounts/count")
        self.assertEqual(count_response.json["count"], 1)

    # Transfer tests (Feature 17)
    def test_incoming_transfer_success(self):
        """Test successful incoming transfer"""
        pesel = "89092909825"
        # Create account with initial balance
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )

        # Perform incoming transfer
        response = self.client.post(
            f"/api/accounts/{pesel}/transfer",
            json={"amount": 500, "type": "incoming"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Zlecenie przyjęto do realizacji"})

        # Verify balance increased
        account_response = self.client.get(f"/api/accounts/{pesel}")
        self.assertEqual(account_response.json["balance"], 500.0)

    def test_outgoing_transfer_success(self):
        """Test successful outgoing transfer with sufficient funds"""
        pesel = "89092909825"
        # Create account
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )

        # Add funds first
        self.client.post(
            f"/api/accounts/{pesel}/transfer", json={"amount": 1000, "type": "incoming"}
        )

        # Perform outgoing transfer
        response = self.client.post(
            f"/api/accounts/{pesel}/transfer",
            json={"amount": 300, "type": "outgoing"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Zlecenie przyjęto do realizacji"})

        # Verify balance decreased
        account_response = self.client.get(f"/api/accounts/{pesel}")
        self.assertEqual(account_response.json["balance"], 700.0)

    def test_express_transfer_success(self):
        """Test successful express transfer with sufficient funds"""
        pesel = "89092909825"
        # Create account
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )

        # Add funds first
        self.client.post(
            f"/api/accounts/{pesel}/transfer", json={"amount": 1000, "type": "incoming"}
        )

        # Perform express transfer (fee is 1.0 for PersonalAccount)
        response = self.client.post(
            f"/api/accounts/{pesel}/transfer",
            json={"amount": 300, "type": "express"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Zlecenie przyjęto do realizacji"})

        # Verify balance decreased by amount + fee
        account_response = self.client.get(f"/api/accounts/{pesel}")
        self.assertEqual(account_response.json["balance"], 699.0)  # 1000 - 300 - 1

    def test_outgoing_transfer_insufficient_funds(self):
        """Test outgoing transfer fails with insufficient funds (422)"""
        pesel = "89092909825"
        # Create account with 0 balance
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )

        # Try outgoing transfer without funds
        response = self.client.post(
            f"/api/accounts/{pesel}/transfer",
            json={"amount": 100, "type": "outgoing"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("error", response.json)
        self.assertIn("Insufficient funds", response.json["error"])

    def test_express_transfer_insufficient_funds(self):
        """Test express transfer fails with insufficient funds (422)"""
        pesel = "89092909825"
        # Create account and add some funds (but not enough for express + fee)
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )
        self.client.post(
            f"/api/accounts/{pesel}/transfer", json={"amount": 50, "type": "incoming"}
        )

        # Try express transfer that would need 100 + 1 (fee) = 101
        response = self.client.post(
            f"/api/accounts/{pesel}/transfer",
            json={"amount": 100, "type": "express"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("error", response.json)

    def test_transfer_account_not_found(self):
        """Test transfer returns 404 when account doesn't exist"""
        response = self.client.post(
            "/api/accounts/99999999999/transfer",
            json={"amount": 100, "type": "incoming"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)
        self.assertIn("Account not found", response.json["error"])

    def test_transfer_invalid_type(self):
        """Test transfer returns 400 for invalid transfer type"""
        pesel = "89092909825"
        # Create account
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )

        # Try invalid transfer type
        response = self.client.post(
            f"/api/accounts/{pesel}/transfer",
            json={"amount": 100, "type": "invalid_type"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertIn("Invalid transfer type", response.json["error"])

    def test_transfer_negative_amount(self):
        """Test transfer returns 400 for negative amount"""
        pesel = "89092909825"
        # Create account
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )

        # Try negative amount
        response = self.client.post(
            f"/api/accounts/{pesel}/transfer",
            json={"amount": -100, "type": "incoming"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertIn("positive number", response.json["error"])

    def test_transfer_zero_amount(self):
        """Test transfer returns 400 for zero amount"""
        pesel = "89092909825"
        # Create account
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )

        # Try zero amount
        response = self.client.post(
            f"/api/accounts/{pesel}/transfer", json={"amount": 0, "type": "incoming"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_transfer_missing_amount(self):
        """Test transfer returns 400 when amount is missing"""
        pesel = "89092909825"
        # Create account
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )

        # Try without amount field
        response = self.client.post(
            f"/api/accounts/{pesel}/transfer", json={"type": "incoming"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertIn("Missing required fields", response.json["error"])

    def test_transfer_missing_type(self):
        """Test transfer returns 400 when type is missing"""
        pesel = "89092909825"
        # Create account
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )

        # Try without type field
        response = self.client.post(
            f"/api/accounts/{pesel}/transfer", json={"amount": 100}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertIn("Missing required fields", response.json["error"])

    def test_transfer_multiple_operations(self):
        """Test multiple transfers and verify balance changes"""
        pesel = "89092909825"
        # Create account
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )

        # Incoming transfer 1000
        self.client.post(
            f"/api/accounts/{pesel}/transfer", json={"amount": 1000, "type": "incoming"}
        )

        # Outgoing transfer 200
        self.client.post(
            f"/api/accounts/{pesel}/transfer", json={"amount": 200, "type": "outgoing"}
        )

        # Express transfer 100 (fee = 1)
        self.client.post(
            f"/api/accounts/{pesel}/transfer", json={"amount": 100, "type": "express"}
        )

        # Incoming transfer 500
        self.client.post(
            f"/api/accounts/{pesel}/transfer", json={"amount": 500, "type": "incoming"}
        )

        # Verify final balance: 1000 - 200 - 100 - 1 + 500 = 1199
        account_response = self.client.get(f"/api/accounts/{pesel}")
        self.assertEqual(account_response.json["balance"], 1199.0)

    def test_transfer_all_types_validation(self):
        """Test all three transfer types work correctly"""
        pesel = "89092909825"
        # Create account
        self.client.post(
            "/api/accounts",
            json={"name": "James", "surname": "Hetfield", "pesel": pesel},
        )

        # Test incoming
        response1 = self.client.post(
            f"/api/accounts/{pesel}/transfer", json={"amount": 1000, "type": "incoming"}
        )
        self.assertEqual(response1.status_code, 200)

        # Test outgoing
        response2 = self.client.post(
            f"/api/accounts/{pesel}/transfer", json={"amount": 300, "type": "outgoing"}
        )
        self.assertEqual(response2.status_code, 200)

        # Test express
        response3 = self.client.post(
            f"/api/accounts/{pesel}/transfer", json={"amount": 200, "type": "express"}
        )
        self.assertEqual(response3.status_code, 200)

        # All should return success message
        self.assertEqual(response1.json["message"], "Zlecenie przyjęto do realizacji")
        self.assertEqual(response2.json["message"], "Zlecenie przyjęto do realizacji")
        self.assertEqual(response3.json["message"], "Zlecenie przyjęto do realizacji")


if __name__ == "__main__":
    unittest.main()
