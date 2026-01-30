import os
from datetime import datetime

import requests

from src.smtp import SMTPClient


class Account:
    balance: float
    express_transfer_fee: float = 0.0

    def __init__(self, balance: float):
        self.balance = balance
        self.historia = []

    def incoming_transfer(self, amount: float):
        if amount > 0:
            self.balance += amount
            self.historia.append(amount)

    def outgoing_transfer(self, amount: float):
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.historia.append(-amount)

    def express_transfer(self, amount: float):
        if 0 < amount <= self.balance:
            total_charge = amount + self.express_transfer_fee
            self.balance -= total_charge
            self.historia.append(-amount)
            self.historia.append(-self.express_transfer_fee)


class PersonalAccount(Account):
    first_name: str
    last_name: str
    pesel: str
    promo_code: str | None
    express_transfer_fee: float = 1.0

    def __init__(
        self,
        first_name: str,
        last_name: str,
        balance: float,
        pesel: str,
        promo_code: str | None = None,
    ):
        super().__init__(balance)
        self.first_name = first_name
        self.last_name = last_name
        self.pesel = pesel
        self.promo_code = promo_code

        if len(pesel) == 11:
            birth_year_prefix = pesel[0:2]
            is_born_in_60s = "60" <= birth_year_prefix <= "69"
        else:
            is_born_in_60s = False

        if (
            self.promo_code is not None
            and self.promo_code.startswith("PROM_")
            and len(self.promo_code) == 8
            and is_born_in_60s
        ):
            self.balance += 50
            self.historia.append(50)

    def _check_loan_condition_1(self) -> bool:
        if len(self.historia) < 3:
            return False
        last_three = self.historia[-3:]
        return all(t > 0 for t in last_three)

    def _check_loan_condition_2(self, amount: float) -> bool:
        if len(self.historia) < 5:
            return False
        sum_last_five = sum(self.historia[-5:])
        return sum_last_five > amount

    def submit_for_loan(self, amount: float) -> bool:
        is_granted = self._check_loan_condition_1() or self._check_loan_condition_2(
            amount
        )

        if is_granted:
            self.balance += amount
            self.historia.append(amount)
            return True
        else:
            return False

    def send_history_via_email(self, email_address: str) -> bool:
        """
        Send account history via email.

        Args:
            email_address: Recipient email address

        Returns:
            True if email was sent successfully, False otherwise
        """
        today = datetime.now().strftime("%Y-%m-%d")
        subject = f"Account Transfer History {today}"
        text = f"Personal account history: {self.historia}"

        smtp_client = SMTPClient()
        return smtp_client.send(subject, text, email_address)


class BusinessAccount(Account):
    company_name: str
    nip: str
    express_transfer_fee: float = 5.0

    def __init__(self, company_name: str, nip: str, promo_code: str | None = None):
        super().__init__(balance=0.0)
        self.company_name = company_name

        if len(nip) == 10 and nip.isdigit():
            self.nip = nip
            # Walidacja NIPu przez API MF
            if not self.validate_nip_in_mf(nip):
                raise ValueError("Company not registered!!")
        else:
            self.nip = "Invalid"

    def validate_nip_in_mf(self, nip: str) -> bool:
        """
        Waliduje NIP przez API Ministerstwa Finansów.
        Zwraca True jeżeli statusVat == "Czynny", False w przeciwnym razie.
        """
        base_url = os.getenv("BANK_APP_MF_URL", "https://wl-test.mf.gov.pl")
        today = datetime.now().strftime("%Y-%m-%d")
        url = f"{base_url}/api/search/nip/{nip}?date={today}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Sprawdzamy czy subject istnieje i czy statusVat == "Czynny"
            subject = data.get("result", {}).get("subject")
            if subject and subject.get("statusVat") == "Czynny":
                return True
            return False
        except Exception:
            return False

    def take_loan(self, amount: float) -> bool:
        condition_1 = self.balance >= (amount * 2)

        condition_2 = -1775 in self.historia

        if condition_1 and condition_2:
            self.balance += amount
            self.historia.append(amount)
            return True
        else:
            return False

    def send_history_via_email(self, email_address: str) -> bool:
        """
        Send account history via email.

        Args:
            email_address: Recipient email address

        Returns:
            True if email was sent successfully, False otherwise
        """
        today = datetime.now().strftime("%Y-%m-%d")
        subject = f"Account Transfer History {today}"
        text = f"Company account history: {self.historia}"

        smtp_client = SMTPClient()
        return smtp_client.send(subject, text, email_address)
