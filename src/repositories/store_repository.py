from src.models.store import Store


STORES_COLLECTION = "stores"


class StoreRepository:
    def __init__(self, firestore_client=None):
        # Allow default construction for easier testing and flexibility.
        # When firestore_client is None, initializes with real Firestore client.
        # This enables dependency injection in tests while providing sensible defaults.
        if firestore_client is None:
            from google.cloud import firestore

            firestore_client = firestore.Client()
        self.firestore_client = firestore_client
    
    def save(self, store: Store):
        # Firestore .add() returns (DocumentReference, WriteResult)
        doc_ref, _ = self.firestore_client.collection(STORES_COLLECTION).add(store.to_dict())
        # Set generated id on the domain object for downstream use
        try:
            store.id = doc_ref.id
        except AttributeError:
            # Store object doesn't allow setting id attribute
            pass
        return doc_ref.id
    
    def get_by_id(self, store_id):
        doc_ref = self.firestore_client.collection(STORES_COLLECTION).document(store_id)
        doc = doc_ref.get()
        if doc.exists:
            store = Store.from_dict(doc.to_dict())
            # propagate id for callers that need it
            store.id = doc.id
            return store
        return None
    
    def find_by_name(self, name):
        docs = (
            self.firestore_client.collection(STORES_COLLECTION)
            .where("name", "==", name)
            .limit(1)
            .stream()
        )
        for doc in docs:
            store = Store.from_dict(doc.to_dict())
            store.id = doc.id
            return store
        return None
    
    def list_all(self):
        docs = self.firestore_client.collection(STORES_COLLECTION).stream()
        stores = []
        for doc in docs:
            s = Store.from_dict(doc.to_dict())
            s.id = doc.id
            stores.append(s)
        return stores

    def update(self, store_id: str, data: dict):
        """Partial update of store document (merge)."""
        doc_ref = self.firestore_client.collection(STORES_COLLECTION).document(store_id)
        # set with merge=True updates only provided fields
        return doc_ref.set(data, merge=True)
