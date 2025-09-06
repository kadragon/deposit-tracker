from decimal import Decimal


class User:
    def __init__(self, name, deposit=0):
        if not name or not name.strip():
            raise ValueError("User name is required")
        deposit_decimal = Decimal(str(deposit))
        if deposit_decimal < 0:
            raise ValueError("Deposit must be non-negative")
        self.name = name
        self.deposit = deposit_decimal
    
    def add_deposit(self, amount):
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Deposit amount must be positive")
        self.deposit += amount_decimal
    
    def subtract_deposit(self, amount):
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount to subtract must be positive")
        if self.deposit < amount_decimal:
            raise ValueError("Insufficient deposit balance")
        self.deposit -= amount_decimal

    def to_dict(self):
        return {"name": self.name, "deposit": str(self.deposit)}

    @classmethod
    def from_dict(cls, data: dict):
        name = data.get("name", "").strip()
        deposit = data.get("deposit", "0")
        return cls(name=name, deposit=deposit)
