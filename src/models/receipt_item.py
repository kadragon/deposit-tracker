from typing import Union, List, Dict
from decimal import Decimal, ROUND_DOWN


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
        self.assigned_users: List['User'] = []

    def calculate_total(self) -> Decimal:
        return self.price * int(self.quantity)

    def assign_to_user(self, user: 'User') -> None:
        """Assign this item to a specific user."""
        # Prevent duplicate assignments which would double-count splits
        if user not in self.assigned_users:
            self.assigned_users.append(user)

    def is_shared(self) -> bool:
        """Check if this item is shared between multiple users."""
        return len(self.assigned_users) > 1

    def calculate_per_user_amounts(self) -> Dict['User', Decimal]:
        """Calculate the amount each assigned user should pay for this item.
        
        Uses ROUND_DOWN to avoid overpaying, with remainder assigned to first user.
        This ensures total always equals the item total exactly.
        """
        if not self.assigned_users:
            return {}
        
        total = self.calculate_total()
        num_users = len(self.assigned_users)
        
        # Calculate base amount per user (rounded down to integer cents)
        base_amount = (total / num_users).quantize(Decimal('1'), rounding=ROUND_DOWN)
        remainder = total - (base_amount * num_users)
        
        # Distribute amounts
        result = {}
        for i, user in enumerate(self.assigned_users):
            if i == 0:  # First user gets the remainder
                result[user] = base_amount + remainder
            else:
                result[user] = base_amount
        
        return result