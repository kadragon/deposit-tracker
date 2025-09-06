from typing import Any, List
from decimal import Decimal


class Receipt:
    """Represents a purchase receipt composed of items for a user at a store."""

    def __init__(self, user: Any, store: Any):
        self.user = user
        self.store = store
        self.items: List[Any] = []  # can contain dicts or ReceiptItem instances

    def add_item(self, name: str, price: Any, quantity: int) -> None:
        """Add an item using primitive fields with basic validation."""
        price_decimal = Decimal(str(price))
        if price_decimal < 0:
            raise ValueError("Item price must be non-negative")
        if quantity < 1:
            raise ValueError("Item quantity must be at least 1")
        item = {
            "name": name,
            "price": price_decimal,
            "quantity": quantity,
        }
        self.items.append(item)

    def add_receipt_item(self, item: Any) -> None:
        """Append a ReceiptItem-like object; kept flexible for test compatibility."""
        self.items.append(item)

    def calculate_total(self) -> Decimal:
        total = Decimal("0")
        for item in self.items:
            # Support both dict items and ReceiptItem-like objects
            if isinstance(item, dict):
                total += Decimal(str(item["price"])) * int(item["quantity"])
            else:
                if hasattr(item, "calculate_total"):
                    total += Decimal(str(item.calculate_total()))
                else:
                    # Fallback for simple objects with price/quantity
                    total += Decimal(str(getattr(item, "price", 0))) * int(
                        getattr(item, "quantity", 1)
                    )
        return total
