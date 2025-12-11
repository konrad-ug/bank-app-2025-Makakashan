from unittest.mock import patch

import pytest

from src.account import BusinessAccount


class TestBusinessAccount:
    @pytest.mark.parametrize(
        #
        "company_name, nip, expected_nip",
        [
            ("Firma Krótka", "123", "Invalid"),
            ("Firma Długa", "12345678901", "Invalid"),
            ("Firma Litery", "123456789A", "Invalid"),
        ],
    )
    def test_business_account_creation_invalid_nip_length(
        self, company_name, nip, expected_nip
    ):
        """Test dla niepoprawnych NIPów - nie wysyłamy requestu"""
        account = BusinessAccount(company_name, nip)
        assert account.company_name == company_name
        assert account.nip == expected_nip
        assert account.balance == 0.0
        assert account.historia == []

    @patch("src.account.requests.get")
    def test_business_account_valid_nip_active(self, mock_get):
        """Test dla poprawnego NIPu z statusem Czynny"""
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"subject": {"nip": "1234567890", "statusVat": "Czynny"}}
        }

        account = BusinessAccount("Firma XYZ", "1234567890")
        assert account.company_name == "Firma XYZ"
        assert account.nip == "1234567890"
        assert account.balance == 0.0
        assert account.historia == []
        mock_get.assert_called_once()

    @patch("src.account.requests.get")
    def test_business_account_nip_not_active(self, mock_get):
        """Test dla NIPu który nie jest czynny - rzuca błąd"""
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"subject": {"nip": "0987654321", "statusVat": "Nieczynny"}}
        }

        with pytest.raises(ValueError, match="Company not registered!!"):
            BusinessAccount("Firma Poprawna", "0987654321")

    @patch("src.account.requests.get")
    def test_business_account_nip_not_found(self, mock_get):
        """Test dla NIPu który nie istnieje w bazie MF"""
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": {"subject": None}}

        with pytest.raises(ValueError, match="Company not registered!!"):
            BusinessAccount("Firma Nieistniejąca", "1111111111")

    @patch("src.account.requests.get")
    def test_business_account_api_error(self, mock_get):
        """Test gdy API zwraca błąd"""
        mock_get.side_effect = Exception("API Error")

        with pytest.raises(ValueError, match="Company not registered!!"):
            BusinessAccount("Firma Test", "9999999999")

    @patch("src.account.requests.get")
    def test_business_account_no_promo_bonus(self, mock_get):
        """Test że kod promocyjny nie działa dla kont firmowych"""
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"subject": {"nip": "1234567890", "statusVat": "Czynny"}}
        }

        account = BusinessAccount("Firma z Kodem", "1234567890", "PROM_123")
        assert account.balance == 0.0
        assert account.historia == []

    def test_validate_nip_in_mf_method(self):
        """Test metody validate_nip_in_mf z mockowaniem"""
        with patch("src.account.requests.get") as mock_get:
            mock_response = mock_get.return_value
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "result": {"subject": {"nip": "8461627563", "statusVat": "Czynny"}}
            }

            account = BusinessAccount("Test Company", "8461627563")
            result = account.validate_nip_in_mf("8461627563")
            assert result is True

    def test_validate_nip_in_mf_returns_false_for_inactive(self):
        """Test że validate_nip_in_mf zwraca False dla nieaktywnych"""
        with patch("src.account.requests.get") as mock_get:
            mock_response = mock_get.return_value
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": {"subject": None}}

            # Musimy stworzyć instancję z poprawnym NIPem najpierw
            with patch("src.account.requests.get") as mock_get_init:
                mock_response_init = mock_get_init.return_value
                mock_response_init.status_code = 200
                mock_response_init.json.return_value = {
                    "result": {"subject": {"nip": "1234567890", "statusVat": "Czynny"}}
                }
                account = BusinessAccount("Test", "1234567890")

            result = account.validate_nip_in_mf("9999999999")
            assert result is False
