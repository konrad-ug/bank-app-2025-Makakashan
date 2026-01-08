#!/usr/bin/env python3
"""
Demo script to demonstrate send_history_via_email functionality.
This script shows how the email history feature works for both
PersonalAccount and BusinessAccount.
"""

from unittest.mock import MagicMock, patch

from src.account import BusinessAccount, PersonalAccount


def demo_personal_account():
    """Demonstrate PersonalAccount email history functionality"""
    print("=" * 60)
    print("DEMO: Personal Account Email History")
    print("=" * 60)

    # Create a personal account
    account = PersonalAccount(
        first_name="Jan", last_name="Kowalski", balance=1000.0, pesel="65010112345"
    )

    # Perform some transactions
    print(f"Initial balance: {account.balance}")
    account.incoming_transfer(100)
    print(f"After incoming transfer of 100: {account.balance}")
    account.outgoing_transfer(1)
    print(f"After outgoing transfer of 1: {account.balance}")
    account.incoming_transfer(500)
    print(f"After incoming transfer of 500: {account.balance}")

    print(f"\nAccount history: {account.historia}")

    # Mock the SMTP client to simulate email sending
    with (
        patch("src.account.SMTPClient") as mock_smtp_class,
        patch("src.account.datetime") as mock_datetime,
    ):
        # Setup mocks
        mock_datetime.now.return_value.strftime.return_value = "2025-01-08"
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance

        # Send email
        email = "jan.kowalski@example.com"
        result = account.send_history_via_email(email)

        # Display results
        print(f"\n--- Email Sending Simulation ---")
        print(f"Email sent successfully: {result}")
        print(f"\nEmail details:")
        call_args = mock_smtp_instance.send.call_args
        print(f"  Subject: {call_args[0][0]}")
        print(f"  Body: {call_args[0][1]}")
        print(f"  To: {call_args[0][2]}")

    print()


def demo_business_account():
    """Demonstrate BusinessAccount email history functionality"""
    print("=" * 60)
    print("DEMO: Business Account Email History")
    print("=" * 60)

    # Mock NIP validation
    with patch("src.account.BusinessAccount.validate_nip_in_mf") as mock_validate:
        mock_validate.return_value = True

        # Create a business account
        account = BusinessAccount(
            company_name="Tech Solutions Sp. z o.o.", nip="1234567890"
        )

        # Perform some transactions
        print(f"Initial balance: {account.balance}")
        account.incoming_transfer(5000)
        print(f"After incoming transfer of 5000: {account.balance}")
        account.outgoing_transfer(1000)
        print(f"After outgoing transfer of 1000: {account.balance}")
        account.incoming_transfer(500)
        print(f"After incoming transfer of 500: {account.balance}")

        print(f"\nAccount history: {account.historia}")

        # Mock the SMTP client to simulate email sending
        with (
            patch("src.account.SMTPClient") as mock_smtp_class,
            patch("src.account.datetime") as mock_datetime,
        ):
            # Setup mocks
            mock_datetime.now.return_value.strftime.return_value = "2025-01-08"
            mock_smtp_instance = MagicMock()
            mock_smtp_instance.send.return_value = True
            mock_smtp_class.return_value = mock_smtp_instance

            # Send email
            email = "accounting@techsolutions.com"
            result = account.send_history_via_email(email)

            # Display results
            print(f"\n--- Email Sending Simulation ---")
            print(f"Email sent successfully: {result}")
            print(f"\nEmail details:")
            call_args = mock_smtp_instance.send.call_args
            print(f"  Subject: {call_args[0][0]}")
            print(f"  Body: {call_args[0][1]}")
            print(f"  To: {call_args[0][2]}")

    print()


def demo_email_failure():
    """Demonstrate handling of email sending failure"""
    print("=" * 60)
    print("DEMO: Email Sending Failure Handling")
    print("=" * 60)

    # Create a personal account
    account = PersonalAccount(
        first_name="Anna", last_name="Nowak", balance=500.0, pesel="85010112345"
    )

    account.incoming_transfer(200)
    account.outgoing_transfer(50)

    print(f"Account balance: {account.balance}")
    print(f"Account history: {account.historia}")

    # Mock SMTP client to return failure
    with (
        patch("src.account.SMTPClient") as mock_smtp_class,
        patch("src.account.datetime") as mock_datetime,
    ):
        # Setup mocks
        mock_datetime.now.return_value.strftime.return_value = "2025-01-08"
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = False  # Simulate failure
        mock_smtp_class.return_value = mock_smtp_instance

        # Try to send email
        email = "anna.nowak@example.com"
        result = account.send_history_via_email(email)

        # Display results
        print(f"\n--- Email Sending Simulation ---")
        print(f"Email sent successfully: {result}")
        print(f"Status: {'SUCCESS' if result else 'FAILED'}")

        if not result:
            print("\nNote: The email could not be sent. Please check:")
            print("  - SMTP server configuration")
            print("  - Network connectivity")
            print("  - Email address validity")

    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  Bank Application - Email History Feature Demo".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")

    # Run demos
    demo_personal_account()
    demo_business_account()
    demo_email_failure()

    print("=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    print("\nFor more details, run the test suite:")
    print("  python -m pytest tests/unit/test_email_history.py -v")
    print()
