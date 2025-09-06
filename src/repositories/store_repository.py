from src.models.store import Store


class StoreRepository:
    def __init__(self, firestore_client):
        self.firestore_client = firestore_client
    
    def save(self, store):
        self.firestore_client.collection("stores")
        return "saved"
    
    def get_by_id(self, store_id):
        doc_ref = self.firestore_client.collection("stores").document(store_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            store = Store(name=data["name"])
            store.coupon_enabled = data["coupon_enabled"]
            store.coupon_goal = data["coupon_goal"]
            return store
        return None
    
    def find_by_name(self, name):
        docs = self.firestore_client.collection("stores").where("name", "==", name).limit(1).stream()
        for doc in docs:
            data = doc.to_dict()
            store = Store(name=data["name"])
            store.coupon_enabled = data["coupon_enabled"]
            store.coupon_goal = data["coupon_goal"]
            return store
        return None