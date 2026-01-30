"""
Performance tests for Bank Account API.
These tests verify that API responses are within acceptable time limits.
"""

import time

import pytest
import requests

BASE_URL = "http://localhost:5000"
TIMEOUT = 0.5  # Maximum response time in seconds


@pytest.fixture(scope="module")
def api_url():
    """Provide the base API URL"""
    return BASE_URL


def test_create_and_delete_account_100_times(api_url):
    """
    Performance test: Create and delete account 100 times.
    Each request should complete within 0.5 seconds.
    """
    pesel_base = "90010112345"

    for i in range(100):
        pesel = f"{i:011d}"

        start_time = time.time()
        create_response = requests.post(
            f"{api_url}/api/accounts",
            json={"name": "Test", "surname": "User", "pesel": pesel},
            timeout=TIMEOUT,
        )
        create_time = time.time() - start_time

        assert create_response.status_code == 201, f"Create failed at iteration {i}"
        assert create_time < TIMEOUT, f"Create took {create_time:.3f}s (iteration {i})"

        start_time = time.time()
        delete_response = requests.delete(
            f"{api_url}/api/accounts/{pesel}", timeout=TIMEOUT
        )
        delete_time = time.time() - start_time

        assert delete_response.status_code == 200, f"Delete failed at iteration {i}"
        assert delete_time < TIMEOUT, f"Delete took {delete_time:.3f}s (iteration {i})"


def test_create_account_and_100_incoming_transfers(api_url):
    """
    Performance test: Create account and perform 100 incoming transfers.
    Each request should complete within 0.5 seconds.
    Final balance should be correct.
    """
    pesel = "85010112345"
    transfer_amount = 100.0
    expected_balance = transfer_amount * 100

    start_time = time.time()
    create_response = requests.post(
        f"{api_url}/api/accounts",
        json={"name": "Transfer", "surname": "Test", "pesel": pesel},
        timeout=TIMEOUT,
    )
    create_time = time.time() - start_time

    assert create_response.status_code == 201, "Account creation failed"
    assert create_time < TIMEOUT, f"Create took {create_time:.3f}s"

    for i in range(100):
        start_time = time.time()
        transfer_response = requests.post(
            f"{api_url}/api/accounts/{pesel}/transfer",
            json={"amount": transfer_amount, "type": "incoming"},
            timeout=TIMEOUT,
        )
        transfer_time = time.time() - start_time

        assert transfer_response.status_code == 200, f"Transfer failed at iteration {i}"
        assert transfer_time < TIMEOUT, (
            f"Transfer took {transfer_time:.3f}s (iteration {i})"
        )

    get_response = requests.get(f"{api_url}/api/accounts/{pesel}", timeout=TIMEOUT)
    assert get_response.status_code == 200, "Failed to get account"

    account_data = get_response.json()
    actual_balance = account_data.get("balance")
    assert actual_balance == expected_balance, (
        f"Expected balance {expected_balance}, got {actual_balance}"
    )

    requests.delete(f"{api_url}/api/accounts/{pesel}", timeout=TIMEOUT)


def test_create_1000_accounts_then_delete_all(api_url):
    """
    BONUS: Performance test - Create 1000 accounts, then delete all.
    This tests bulk operations differently than create-delete cycles.

    Difference from create-delete test:
    - This test creates ALL accounts first, keeping them in memory/registry
    - Tests system behavior with large dataset (memory usage, lookup performance)
    - Then deletes all accounts from populated state
    - Simulates real-world scenario where system has many active accounts

    The create-delete test operates on minimal state (1 account at a time),
    while this test stresses the system with full dataset throughout creation phase.
    """
    num_accounts = 1000
    pesels = []

    for i in range(num_accounts):
        pesel = f"{i:011d}"
        pesels.append(pesel)

        start_time = time.time()
        create_response = requests.post(
            f"{api_url}/api/accounts",
            json={"name": "Bulk", "surname": f"User{i}", "pesel": pesel},
            timeout=TIMEOUT,
        )
        create_time = time.time() - start_time

        assert create_response.status_code == 201, f"Create failed at account {i}"
        assert create_time < TIMEOUT, f"Create took {create_time:.3f}s (account {i})"

    get_all_response = requests.get(f"{api_url}/api/accounts", timeout=1.0)
    assert get_all_response.status_code == 200
    assert len(get_all_response.json()) == num_accounts, (
        f"Expected {num_accounts} accounts, found {len(get_all_response.json())}"
    )

    for i, pesel in enumerate(pesels):
        start_time = time.time()
        delete_response = requests.delete(
            f"{api_url}/api/accounts/{pesel}", timeout=TIMEOUT
        )
        delete_time = time.time() - start_time

        assert delete_response.status_code == 200, f"Delete failed at account {i}"
        assert delete_time < TIMEOUT, f"Delete took {delete_time:.3f}s (account {i})"

    get_all_response = requests.get(f"{api_url}/api/accounts", timeout=1.0)
    assert get_all_response.status_code == 200
    assert len(get_all_response.json()) == 0, "Not all accounts were deleted"
