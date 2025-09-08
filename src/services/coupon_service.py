class CouponService:
    def __init__(self, coupon_repository, store_repository):
        self.coupon_repository = coupon_repository
        self.store_repository = store_repository

    def award_coupon_for_purchase(self, user_id: str, store_id: str):
        store = self.store_repository.get_by_id(store_id)
        if store is None or not store.coupon_enabled:
            return
        # Delegate atomic/consistency concerns to repository
        self.coupon_repository.increment(user_id, store_id, store.coupon_goal)

    def award_coupons_for_split_payment(self, store_id: str, split_transactions: dict):
        """Award coupons only to users who actually paid (non-zero amounts)."""
        store = self.store_repository.get_by_id(store_id)
        if store is None or not store.coupon_enabled:
            return
        
        # Only award coupons to users with non-zero payment amounts
        for user_id, amount_str in split_transactions.items():
            # Convert string amount to number for comparison
            try:
                if float(amount_str) > 0:
                    self.coupon_repository.increment(user_id, store_id, store.coupon_goal)
            except (ValueError, TypeError):
                pass

    # Backward-compatible alias used by some callers/tests
    def award_coupon(self, user_id: str, store_id: str):
        return self.award_coupon_for_purchase(user_id, store_id)
