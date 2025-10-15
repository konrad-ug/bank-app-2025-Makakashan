class Account:
    first_name: str
    last_name: str
    balance: float
    pesel: str
    promo_code: str | None = None

    def __init__(
        self,
        first_name: str,
        last_name: str,
        balance: float,
        pesel: str,
        promo_code: str | None = None,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.balance = balance
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
