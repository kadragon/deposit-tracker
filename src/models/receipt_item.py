from typing import Union, List, Any, Dict
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
        self.assigned_users: List[Any] = []

    def calculate_total(self) -> Decimal:
        return self.price * int(self.quantity)

    def assign_to_user(self, user: Any) -> None:
        """Assign this item to a specific user."""
        self.assigned_users.append(user)

    def is_shared(self) -> bool:
        """Check if this item is shared between multiple users."""
        return len(self.assigned_users) > 1

    def calculate_per_user_amounts(self) -> Dict[Any, Decimal]:
        """Calculate the amount each assigned user should pay for this item."""
        if not self.assigned_users:
            return {}
        
        total = self.calculate_total()
        per_user_amount = total / len(self.assigned_users)
        
        return {user: per_user_amount for user in self.assigned_users}
