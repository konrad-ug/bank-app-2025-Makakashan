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

        elif amount > 0 and self.balance == amount:
            self.balance -= amount + self.express_transfer_fee
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


class BusinessAccount(Account):
    company_name: str
    nip: str
    express_transfer_fee: float = 5.0

    def __init__(self, company_name: str, nip: str, promo_code: str | None = None):
        super().__init__(balance=0.0)
        self.company_name = company_name

        if len(nip) == 10 and nip.isdigit():
            self.nip = nip
        else:
            self.nip = "Invalid"
