from src.models.coupon import Coupon


COUPONS_COLLECTION = "coupons"


class CouponRepository:
    def __init__(self, firestore_client):
        self.firestore_client = firestore_client
    
    def save(self, coupon: Coupon):
        # Firestore .add() returns (DocumentReference, WriteResult)
        doc_ref, _ = self.firestore_client.collection(COUPONS_COLLECTION).add(coupon.to_dict())
        return getattr(doc_ref, "id", None)
    
    def get_by_user(self, user_id: str):
        docs = (
            self.firestore_client.collection(COUPONS_COLLECTION)
            .where("user_id", "==", user_id)
            .stream()
        )
        results = []
        for doc in docs:
            coupon = Coupon.from_dict(doc.to_dict())
            # Preserve document id if available
            if hasattr(doc, "id"):
                coupon.id = doc.id
            results.append(coupon)
        return results
    
    def get_by_user_and_store(self, user_id: str, store_id: str):
        docs = (
            self.firestore_client.collection(COUPONS_COLLECTION)
            .where("user_id", "==", user_id)
            .where("store_id", "==", store_id)
            .limit(1)
            .stream()
        )
        for doc in docs:
            coupon = Coupon.from_dict(doc.to_dict())
            if hasattr(doc, "id"):
                coupon.id = doc.id
            return coupon
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

    def increment(self, user_id: str, store_id: str, goal: int | None = None):
        """Increment coupon count and reset to 0 when reaching goal.

        Note: Firestore transactions or atomic increments are preferred for concurrency.
        This implementation performs a read-modify-write; adapt to transactions in production.
        Returns the resulting count after operation.
        """
        coll = self.firestore_client.collection(COUPONS_COLLECTION)
        docs = (
            coll.where("user_id", "==", user_id)
                .where("store_id", "==", store_id)
                .limit(1)
                .stream()
        )
        for doc in docs:
            data = doc.to_dict() if hasattr(doc, "to_dict") else {}
            current = int(data.get("count", 0))
            new_count = current + 1
            if goal and goal > 0 and new_count >= goal:
                coll.document(doc.id).update({"count": 0})
                return 0
            else:
                coll.document(doc.id).update({"count": new_count})
                return new_count

        # If no existing coupon, create one
        initial = 0 if goal and goal == 1 else 1
        new_coupon = Coupon(user_id, store_id, initial)
        self.save(new_coupon)
        return initial
