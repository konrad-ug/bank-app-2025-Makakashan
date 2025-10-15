class Account:
    first_name: str
    last_name: str
    balance: float

    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name
        self.balance = 0.0
