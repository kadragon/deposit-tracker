from src.models.coupon import Coupon


COUPONS_COLLECTION = "coupons"


class CouponRepository:
    def __init__(self, firestore_client):
        self.firestore_client = firestore_client
    
    def save(self, coupon: Coupon):
        ref = self.firestore_client.collection(COUPONS_COLLECTION).add(coupon.to_dict())
        return getattr(ref, "id", None)
    
    def get_by_user(self, user_id: str):
        docs = (
            self.firestore_client.collection(COUPONS_COLLECTION)
            .where("user_id", "==", user_id)
            .stream()
        )
        return [Coupon.from_dict(doc.to_dict()) for doc in docs]
    
    def get_by_user_and_store(self, user_id: str, store_id: str):
        docs = (
            self.firestore_client.collection(COUPONS_COLLECTION)
            .where("user_id", "==", user_id)
            .where("store_id", "==", store_id)
            .limit(1)
            .stream()
        )
        for doc in docs:
            return Coupon.from_dict(doc.to_dict())
        # If no coupon exists, create a new one with count 0
        return Coupon(user_id, store_id, 0)
    
    def update_count(self, user_id: str, store_id: str, count: int):
        docs = (
            self.firestore_client.collection(COUPONS_COLLECTION)
            .where("user_id", "==", user_id)
            .where("store_id", "==", store_id)
            .limit(1)
            .stream()
        )
        for doc in docs:
            self.firestore_client.collection(COUPONS_COLLECTION).document(doc.id).update({"count": count})
            return
        # If no coupon exists, create one
        new_coupon = Coupon(user_id, store_id, count)
        self.save(new_coupon)