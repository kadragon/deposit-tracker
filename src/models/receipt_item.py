from typing import Union
from decimal import Decimal


class ReceiptItem:
    def __init__(self, name: str, price: Union[int, float, str, Decimal], quantity: int = 1) -> None:
        # Convert to Decimal via string to avoid float precision issues
        price_decimal = Decimal(str(price))
        if price_decimal < 0:
            raise ValueError("Item price must be non-negative")
        if quantity < 1:
            raise ValueError("Item quantity must be at least 1")
        self.name: str = name
        self.price: Decimal = price_decimal
        self.quantity: int = quantity

    def calculate_total(self) -> Decimal:
        return self.price * int(self.quantity)
