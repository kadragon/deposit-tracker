from typing import Dict
from decimal import Decimal
from collections import defaultdict
from src.models.receipt import Receipt


class SplitService:
    """Service for handling receipt splitting logic."""
    
    def split_receipt_by_user_assignment(self, receipt: Receipt) -> Dict['User', Decimal]:
        """Split receipt items based on user assignments and return amounts per user."""
        user_amounts = defaultdict(Decimal)
        
        for item in receipt.items:
            item_user_amounts = item.calculate_per_user_amounts()
            
            for user, amount in item_user_amounts.items():
                user_amounts[user] += amount
        
        return dict(user_amounts)

    def calculate_individual_amounts(self, receipt: Receipt) -> Dict['User', Decimal]:
        """Calculate amounts for items assigned to individual users (no sharing)."""
        user_amounts = defaultdict(Decimal)
        
        for item in receipt.items:
            # Only process non-shared items (assigned to exactly one user)
            if not item.is_shared() and item.assigned_users:
                user = item.assigned_users[0]
                amount = item.calculate_total()
                user_amounts[user] += amount
        
        return dict(user_amounts)

    def validate_all_items_assigned(self, receipt: Receipt) -> bool:
        """Validate that all items in the receipt have been assigned to users."""
        return all(item.assigned_users for item in receipt.items)

    def handle_shared_items_proportionally(self, receipt: Receipt) -> Dict['User', Decimal]:
        """Calculate amounts for items that are shared between users."""
        user_amounts = defaultdict(Decimal)
        
        for item in receipt.items:
            # Only process shared items (assigned to more than one user)
            if item.is_shared():
                item_user_amounts = item.calculate_per_user_amounts()
                
                for user, amount in item_user_amounts.items():
                    user_amounts[user] += amount
        
        return dict(user_amounts)