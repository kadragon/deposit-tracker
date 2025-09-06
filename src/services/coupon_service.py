class CouponService:
    def __init__(self, coupon_repository, store_repository):
        self.coupon_repository = coupon_repository
        self.store_repository = store_repository
    
    def award_coupon_for_purchase(self, user_id: str, store_id: str):
        store = self.store_repository.get_by_id(store_id)
        if not store.coupon_enabled:
            return
        
        coupon = self.coupon_repository.get_by_user_and_store(user_id, store_id)
        coupon.increment_count()
        
        if coupon.is_goal_reached(store.coupon_goal):
            # Reset coupon when goal is reached
            self.coupon_repository.update_count(user_id, store_id, 0)
        else:
            self.coupon_repository.update_count(user_id, store_id, coupon.count)