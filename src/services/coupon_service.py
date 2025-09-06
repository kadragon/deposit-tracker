class CouponService:
    def __init__(self, coupon_repository, store_repository):
        self.coupon_repository = coupon_repository
        self.store_repository = store_repository
    
    def award_coupon_for_purchase(self, user_id: str, store_id: str):
        store = self.store_repository.get_by_id(store_id)
        if not store.coupon_enabled:
            return
        # Delegate atomic/consistency concerns to repository
        self.coupon_repository.increment(user_id, store_id, store.coupon_goal)
