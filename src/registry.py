from .account import PersonalAccount  # [cite: 38]


class AccountRegistry:
    def __init__(self):
        self.accounts: list[PersonalAccount] = []

    def add_account(self, account: PersonalAccount):
        self.accounts.append(account)

    def find_account_by_pesel(self, pesel: str) -> PersonalAccount | None:
        for account in self.accounts:
            if account.pesel == pesel:
                return account
        return None

    def get_all_accounts(self) -> list[PersonalAccount]:
        return self.accounts

    def get_account_count(self) -> int:
        return len(self.accounts)
