from typing import Any, List, Dict, Optional
from decimal import Decimal
from src.models.receipt_item import ReceiptItem


class Receipt:
    """Represents a purchase receipt composed of items for a user at a store."""

    def __init__(self, user: Any, store: Any, purchase_date: Optional[str] = None):
        self.user = user
        self.store = store
        self.items: List[ReceiptItem] = []
        self.purchase_date = purchase_date

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

    def to_dict(self) -> Dict[str, Any]:
        """Domain-level serialization (not persistence-specific).

        Uses integers for KRW to reflect whole unit amounts. Persistence layers
        may override this to preserve precision as strings.
        """
        return {
            "user": getattr(self.user, "name", None),
            "store": getattr(self.store, "name", None),
            "items": [
                {"name": i.name, "price": int(i.price), "quantity": i.quantity}
                for i in self.items
            ],
            "total": int(self.calculate_total()),
            "purchase_date": self.purchase_date,
        }

    def to_firestore_dict(
        self,
        *,
        user_id: str | None = None,
        store_id: str | None = None,
        created_at: Any | None = None,
    ) -> Dict[str, Any]:
        """Serialize for Firestore storage.

        - user_id/store_id default to bound object's id attribute when omitted
        - price/total are strings to avoid precision issues in Firestore
        - created_at is passed in by repository (e.g., SERVER_TIMESTAMP)
        """
        uid = user_id if user_id is not None else getattr(self.user, "id", None)
        sid = store_id if store_id is not None else getattr(self.store, "id", None)
        data: Dict[str, Any] = {
            "user_id": uid,
            "store_id": sid,
            "items": [
                {"name": i.name, "price": str(i.price), "quantity": i.quantity}
                for i in self.items
            ],
            "total": str(self.calculate_total()),
            "purchase_date": self.purchase_date,
        }
        if created_at is not None:
            data["created_at"] = created_at
        return data
