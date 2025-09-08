from typing import Any, List, Optional
from datetime import datetime
from google.cloud import firestore


class ReceiptRepository:
    def __init__(self, client: Optional[firestore.Client] = None):
        # Allow dependency injection for easier testing and configurability
        self.db = client or firestore.Client()
    
    def save(self, receipt: Any) -> str:
        # Use model-provided serializer for Firestore mapping
        receipt_data = receipt.to_firestore_dict(
            user_id=getattr(receipt.user, "id", None),
            store_id=getattr(receipt.store, "id", None),
            created_at=firestore.SERVER_TIMESTAMP,
        )

        # Enrich for admin/dashboard queries that expect denormalized fields
        try:
            receipt_data["user_name"] = getattr(receipt.user, "name", None)
        except (AttributeError, TypeError):
            receipt_data["user_name"] = None
            
        try:
            receipt_data["store_name"] = getattr(receipt.store, "name", None)
        except (AttributeError, TypeError):
            receipt_data["store_name"] = None
            
        # Provide an alias for total used by some views
        receipt_data["total_amount"] = receipt_data.get("total")

        doc_ref, _ = self.db.collection("receipts").add(receipt_data)
        return doc_ref.id
    
    def _doc_to_dict(self, doc) -> dict:
        """Convert Firestore document to dictionary with id."""
        receipt_data = doc.to_dict()
        receipt_data["id"] = doc.id
        return receipt_data
    
    def find_by_user_id(self, user_id: str) -> List[dict]:
        docs = self.db.collection("receipts").where("user_id", "==", user_id).get()
        return [self._doc_to_dict(doc) for doc in docs]
    
    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[dict]:
        docs = (self.db.collection("receipts")
                .where("created_at", ">=", start_date)
                .where("created_at", "<=", end_date)
                .get())
        return [self._doc_to_dict(doc) for doc in docs]
    
    def list_all(self) -> List[dict]:
        docs = self.db.collection("receipts").get()
        return [self._doc_to_dict(doc) for doc in docs]
    
    def find_by_store_name(self, store_name: str) -> List[dict]:
        docs = self.db.collection("receipts").where("store_name", "==", store_name).get()
        return [self._doc_to_dict(doc) for doc in docs]
    
    def find_by_uploader(self, uploader_id: str) -> List[dict]:
        docs = self.db.collection("receipts").where("user_id", "==", uploader_id).get()
        return [self._doc_to_dict(doc) for doc in docs]
    
    def find_split_transactions_by_user(self, user_id: str) -> List[dict]:
        # Query for receipts where the user has a split transaction
        docs = self.db.collection("receipts").where(f"split_transactions.{user_id}", ">=", "").get()
        
        transactions = []
        for doc in docs:
            receipt_data = doc.to_dict()
            # The query on line 67 already ensures user_id is in split_transactions,
            # so the conditional check is not necessary.
            split_transactions = receipt_data.get("split_transactions", {})

            transaction = {
                "receipt_id": doc.id,
                "user_amount": split_transactions[user_id],
                "total_amount": receipt_data.get("total"),
                "store_id": receipt_data.get("store_id"),
                "store_name": receipt_data.get("store_name"),
                "created_at": receipt_data.get("created_at")
            }
            transactions.append(transaction)
        
        return transactions
    
    def find_pending_split_requests(self, user_id: str) -> List[dict]:
        # Find receipts where user is a participant but no split transaction recorded yet
        docs = self.db.collection("receipts").where("participants", "array-contains", user_id).get()
        
        pending_requests = []
        for doc in docs:
            receipt_data = doc.to_dict()
            split_transactions = receipt_data.get("split_transactions", {})
            
            # Skip if user already has a split transaction recorded
            if user_id in split_transactions:
                continue
                
            request = {
                "id": doc.id,
                "store_name": receipt_data.get("store_name"),
                "total_amount": receipt_data.get("total"),
                "uploader_name": receipt_data.get("user_name"),
                "created_at": receipt_data.get("created_at")
            }
            pending_requests.append(request)
            
        return pending_requests
