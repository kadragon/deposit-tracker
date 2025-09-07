from src.models.store import Store


STORES_COLLECTION = "stores"


class StoreRepository:
    def __init__(self, firestore_client):
        self.firestore_client = firestore_client
    
    def save(self, store: Store):
        # Firestore .add() returns (DocumentReference, WriteResult)
        doc_ref, _ = self.firestore_client.collection(STORES_COLLECTION).add(store.to_dict())
        return doc_ref.id
    
    def get_by_id(self, store_id):
        doc_ref = self.firestore_client.collection(STORES_COLLECTION).document(store_id)
        doc = doc_ref.get()
        if doc.exists:
            return Store.from_dict(doc.to_dict())
        return None
    
    def find_by_name(self, name):
        docs = (
            self.firestore_client.collection(STORES_COLLECTION)
            .where("name", "==", name)
            .limit(1)
            .stream()
        )
        for doc in docs:
            return Store.from_dict(doc.to_dict())
        return None
