from typing import Any, List
from decimal import Decimal
from src.models.receipt_item import ReceiptItem


class Receipt:
    """Represents a purchase receipt composed of items for a user at a store."""

    def __init__(self, user: Any, store: Any):
        self.user = user
        self.store = store
        self.items: List[ReceiptItem] = []

    def add_item(self, name: str, price: Any, quantity: int) -> None:
        """Add an item by creating a ReceiptItem."""
        item = ReceiptItem(name=name, price=price, quantity=quantity)
        self.add_receipt_item(item)

    def add_receipt_item(self, item: ReceiptItem) -> None:
        """Append a ReceiptItem object."""
        self.items.append(item)

    def calculate_total(self) -> Decimal:
        """Calculates total amount from all receipt items."""
        return sum((item.calculate_total() for item in self.items), Decimal("0"))
