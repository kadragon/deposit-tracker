from src.models.user import User


class UserRepository:
    def __init__(self, firestore_client):
        self.firestore_client = firestore_client
    
    def save(self, user):
        self.firestore_client.collection("users")
        return "saved"
    
    def get_by_id(self, user_id):
        doc_ref = self.firestore_client.collection("users").document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            return User(name=data["name"], deposit=data["deposit"])
        return None
    
    def list_all(self):
        docs = self.firestore_client.collection("users").stream()
        users = []
        for doc in docs:
            data = doc.to_dict()
            users.append(User(name=data["name"], deposit=data["deposit"]))
        return users