from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.account import BusinessAccount, PersonalAccount


class TestPersonalAccountEmailHistory:
    """Tests for PersonalAccount.send_history_via_email method"""

    @patch("src.account.SMTPClient")
    @patch("src.account.datetime")
    def test_send_history_via_email_called_with_correct_params(
        self, mock_datetime, mock_smtp_class
    ):
        """Test that SMTPClient.send is called with correct parameters"""
        mock_datetime.now.return_value.strftime.return_value = "2025-01-08"
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance

        account = PersonalAccount("Jan", "Kowalski", 1000.0, "65010112345")
        account.incoming_transfer(100)
        account.outgoing_transfer(50)

        result = account.send_history_via_email("test@example.com")

        mock_smtp_instance.send.assert_called_once_with(
            "Account Transfer History 2025-01-08",
            "Personal account history: [100, -50]",
            "test@example.com",
        )
        assert result is True

    @patch("src.account.SMTPClient")
    @patch("src.account.datetime")
    def test_send_history_via_email_returns_true_on_success(
        self, mock_datetime, mock_smtp_class
    ):
        """Test that method returns True when email is sent successfully"""
        mock_datetime.now.return_value.strftime.return_value = "2025-01-08"
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance

        account = PersonalAccount("Jan", "Kowalski", 1000.0, "65010112345")
        account.incoming_transfer(500)

        result = account.send_history_via_email("test@example.com")

        assert result is True
        assert mock_smtp_instance.send.call_count == 1

    @patch("src.account.SMTPClient")
    @patch("src.account.datetime")
    def test_send_history_via_email_returns_false_on_failure(
        self, mock_datetime, mock_smtp_class
    ):
        """Test that method returns False when email sending fails"""
        mock_datetime.now.return_value.strftime.return_value = "2025-01-08"
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = False
        mock_smtp_class.return_value = mock_smtp_instance

        account = PersonalAccount("Jan", "Kowalski", 1000.0, "65010112345")
        account.outgoing_transfer(100)

        result = account.send_history_via_email("test@example.com")

        assert result is False
        assert mock_smtp_instance.send.call_count == 1

    @patch("src.account.SMTPClient")
    @patch("src.account.datetime")
    def test_send_history_with_empty_history(self, mock_datetime, mock_smtp_class):
        """Test sending email with empty account history"""
        mock_datetime.now.return_value.strftime.return_value = "2025-01-08"
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance

        account = PersonalAccount("Jan", "Kowalski", 1000.0, "65010112345")

        result = account.send_history_via_email("test@example.com")

        mock_smtp_instance.send.assert_called_once_with(
            "Account Transfer History 2025-01-08",
            "Personal account history: []",
            "test@example.com",
        )
        assert result is True

    @patch("src.account.SMTPClient")
    @patch("src.account.datetime")
    def test_send_history_with_multiple_transfers(self, mock_datetime, mock_smtp_class):
        """Test sending email with multiple transfers in history"""
        mock_datetime.now.return_value.strftime.return_value = "2025-12-10"
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance

        account = PersonalAccount("Jan", "Kowalski", 1000.0, "65010112345")
        account.incoming_transfer(100)
        account.outgoing_transfer(1)
        account.incoming_transfer(500)

        result = account.send_history_via_email("jan@example.com")

        mock_smtp_instance.send.assert_called_once_with(
            "Account Transfer History 2025-12-10",
            "Personal account history: [100, -1, 500]",
            "jan@example.com",
        )
        assert result is True


class TestBusinessAccountEmailHistory:
    """Tests for BusinessAccount.send_history_via_email method"""

    @patch("src.account.BusinessAccount.validate_nip_in_mf")
    @patch("src.account.SMTPClient")
    @patch("src.account.datetime")
    def test_send_history_via_email_called_with_correct_params(
        self, mock_datetime, mock_smtp_class, mock_validate_nip
    ):
        """Test that SMTPClient.send is called with correct parameters for business account"""
        mock_validate_nip.return_value = True
        mock_datetime.now.return_value.strftime.return_value = "2025-01-08"
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance

        account = BusinessAccount("Test Company", "1234567890")
        account.incoming_transfer(5000)
        account.outgoing_transfer(1000)
        account.incoming_transfer(500)

        result = account.send_history_via_email("company@example.com")

        mock_smtp_instance.send.assert_called_once_with(
            "Account Transfer History 2025-01-08",
            "Company account history: [5000, -1000, 500]",
            "company@example.com",
        )
        assert result is True

    @patch("src.account.BusinessAccount.validate_nip_in_mf")
    @patch("src.account.SMTPClient")
    @patch("src.account.datetime")
    def test_send_history_via_email_returns_true_on_success(
        self, mock_datetime, mock_smtp_class, mock_validate_nip
    ):
        """Test that method returns True when email is sent successfully"""
        mock_validate_nip.return_value = True
        mock_datetime.now.return_value.strftime.return_value = "2025-01-08"
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance

        account = BusinessAccount("Test Company", "1234567890")
        account.incoming_transfer(10000)

        result = account.send_history_via_email("company@example.com")

        assert result is True
        assert mock_smtp_instance.send.call_count == 1

    @patch("src.account.BusinessAccount.validate_nip_in_mf")
    @patch("src.account.SMTPClient")
    @patch("src.account.datetime")
    def test_send_history_via_email_returns_false_on_failure(
        self, mock_datetime, mock_smtp_class, mock_validate_nip
    ):
        """Test that method returns False when email sending fails"""
        mock_validate_nip.return_value = True
        mock_datetime.now.return_value.strftime.return_value = "2025-01-08"
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = False
        mock_smtp_class.return_value = mock_smtp_instance

        account = BusinessAccount("Test Company", "1234567890")
        account.incoming_transfer(5000)

        result = account.send_history_via_email("company@example.com")

        assert result is False
        assert mock_smtp_instance.send.call_count == 1

    @patch("src.account.BusinessAccount.validate_nip_in_mf")
    @patch("src.account.SMTPClient")
    @patch("src.account.datetime")
    def test_send_history_with_empty_history(
        self, mock_datetime, mock_smtp_class, mock_validate_nip
    ):
        """Test sending email with empty business account history"""
        mock_validate_nip.return_value = True
        mock_datetime.now.return_value.strftime.return_value = "2025-01-08"
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance

        account = BusinessAccount("Test Company", "1234567890")

        result = account.send_history_via_email("company@example.com")

        mock_smtp_instance.send.assert_called_once_with(
            "Account Transfer History 2025-01-08",
            "Company account history: []",
            "company@example.com",
        )
        assert result is True

    @patch("src.account.BusinessAccount.validate_nip_in_mf")
    @patch("src.account.SMTPClient")
    @patch("src.account.datetime")
    def test_send_history_with_different_date_format(
        self, mock_datetime, mock_smtp_class, mock_validate_nip
    ):
        """Test that date format is correct (YYYY-MM-DD)"""
        mock_validate_nip.return_value = True
        mock_datetime.now.return_value.strftime.return_value = "2025-12-25"
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance

        account = BusinessAccount("Test Company", "1234567890")
        account.incoming_transfer(1000)

        result = account.send_history_via_email("test@example.com")

        assert (
            mock_smtp_instance.send.call_args[0][0]
            == "Account Transfer History 2025-12-25"
        )
        assert result is True

    @patch("src.account.BusinessAccount.validate_nip_in_mf")
    @patch("src.account.SMTPClient")
    @patch("src.account.datetime")
    def test_send_history_verifies_call_args(
        self, mock_datetime, mock_smtp_class, mock_validate_nip
    ):
        """Test using call_args to verify method was called with correct arguments"""
        mock_validate_nip.return_value = True
        mock_datetime.now.return_value.strftime.return_value = "2025-01-08"
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance

        account = BusinessAccount("Test Company", "1234567890")
        account.incoming_transfer(5000)
        account.outgoing_transfer(1000)

        result = account.send_history_via_email("business@example.com")

        call_args = mock_smtp_instance.send.call_args
        assert call_args[0][0] == "Account Transfer History 2025-01-08"
        assert call_args[0][1] == "Company account history: [5000, -1000]"
        assert call_args[0][2] == "business@example.com"
        assert result is True
