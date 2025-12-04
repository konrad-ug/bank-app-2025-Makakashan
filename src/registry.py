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

    def update_account(
        self, pesel: str, first_name: str = None, last_name: str = None
    ) -> PersonalAccount | None:
        account = self.find_account_by_pesel(pesel)
        if account is None:
            return None

        if first_name is not None:
            account.first_name = first_name
        if last_name is not None:
            account.last_name = last_name

        return account

    def delete_account(self, pesel: str) -> bool:
        account = self.find_account_by_pesel(pesel)
        if account is None:
            return False

        self.accounts.remove(account)
        return True
