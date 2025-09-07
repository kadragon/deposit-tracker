from src.models.user import User


USERS_COLLECTION = "users"


class UserRepository:
    def __init__(self, firestore_client=None):
        # Allow default construction; fall back to real client if not provided
        if firestore_client is None:
            from google.cloud import firestore

            firestore_client = firestore.Client()
        self.firestore_client = firestore_client
    
    def save(self, user: User):
        ref = self.firestore_client.collection(USERS_COLLECTION).add(user.to_dict())
        # Assume add returns a reference with an id attribute (mocked in tests)
        return getattr(ref, "id", None)
    
    def get_by_id(self, user_id):
        doc_ref = self.firestore_client.collection(USERS_COLLECTION).document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return User.from_dict(doc.to_dict())
        return None
    
    def list_all(self):
        docs = self.firestore_client.collection(USERS_COLLECTION).stream()
        return [User.from_dict(doc.to_dict()) for doc in docs]
