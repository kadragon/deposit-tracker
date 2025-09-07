from decimal import Decimal
from typing import Dict


class User:
    def __init__(self, name: str, deposit: int | str | float = 0):
        if not name or not name.strip():
            raise ValueError("User name is required")
        deposit_decimal = Decimal(str(deposit))
        if deposit_decimal < 0:
            raise ValueError("Deposit must be non-negative")
        self.name: str = name
        self.deposit: Decimal = deposit_decimal
    
    def add_deposit(self, amount: int | str | float) -> None:
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Deposit amount must be positive")
        self.deposit += amount_decimal
    
    def subtract_deposit(self, amount: int | str | float) -> None:
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount to subtract must be positive")
        if self.deposit < amount_decimal:
            raise ValueError("Insufficient deposit balance")
        self.deposit -= amount_decimal

    def to_dict(self) -> Dict[str, int | str]:
        # Expose deposit as int for external mapping consistency
        return {"name": self.name, "deposit": int(self.deposit)}

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        name = data.get("name", "").strip()
        deposit = data.get("deposit", "0")
        return cls(name=name, deposit=deposit)
