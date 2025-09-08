from src.models.coupon import Coupon


COUPONS_COLLECTION = "coupons"


class CouponRepository:
    def __init__(self, firestore_client=None):
        # Allow default construction for easier testing and flexibility.
        # When firestore_client is None, initializes with real Firestore client.
        # This enables dependency injection in tests while providing sensible defaults.
        if firestore_client is None:
            from google.cloud import firestore

            firestore_client = firestore.Client()
        self.firestore_client = firestore_client

    def save(self, coupon: Coupon):
        # Firestore .add() returns (DocumentReference, WriteResult)
        doc_ref, _ = self.firestore_client.collection(
            COUPONS_COLLECTION).add(coupon.to_dict())
        return getattr(doc_ref, "id", None)

    def get_by_user(self, user_id: str):
        docs = (
            self.firestore_client.collection(COUPONS_COLLECTION)
            .where("user_id", "==", user_id)
            .stream()
        )
        results = []
        for doc in docs:
            coupon = Coupon.from_dict(doc.to_dict(), doc.id)
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
            return Coupon.from_dict(doc.to_dict(), doc.id)
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
            self.firestore_client.collection(COUPONS_COLLECTION).document(
                doc.id).update({"count": count})
            return
        # If no coupon exists, create one
        new_coupon = Coupon(user_id, store_id, count)
        self.save(new_coupon)

    def increment(self, user_id: str, store_id: str, goal: int | None = None):
        """Increment coupon count and reset to 0 when reaching goal.

        Uses Firestore transactions to ensure atomicity and prevent race
        conditions. Returns the resulting count after operation.
        """
        from google.cloud.firestore import transactional

        @transactional
        def update_in_transaction(transaction):
            coll = self.firestore_client.collection(COUPONS_COLLECTION)
            docs = list(
                coll.where("user_id", "==", user_id)
                    .where("store_id", "==", store_id)
                    .limit(1)
                    .stream()
            )

            if docs:
                doc = docs[0]
                doc_ref = coll.document(doc.id)
                current_data = transaction.get(doc_ref).to_dict()
                current = int(current_data.get("count", 0))
                new_count = current + 1

                if goal and goal > 0 and new_count >= goal:
                    transaction.update(doc_ref, {"count": 0})
                    return 0
                else:
                    transaction.update(doc_ref, {"count": new_count})
                    return new_count
            else:
                # If no existing coupon, create one
                initial = 0 if goal and goal == 1 else 1
                new_coupon = Coupon(user_id, store_id, initial)
                doc_ref = coll.document()  # Generate new document reference
                transaction.set(doc_ref, new_coupon.to_dict())
                return initial

        transaction = self.firestore_client.transaction()
        return update_in_transaction(transaction)
