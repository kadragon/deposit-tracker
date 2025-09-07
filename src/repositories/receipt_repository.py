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

        doc_ref, _ = self.db.collection("receipts").add(receipt_data)
        return doc_ref.id
    
    def find_by_user_id(self, user_id: str) -> List[dict]:
        docs = self.db.collection("receipts").where("user_id", "==", user_id).get()
        receipts = []
        for doc in docs:
            receipt_data = doc.to_dict()
            receipt_data["id"] = doc.id
            receipts.append(receipt_data)
        return receipts
    
    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[dict]:
        docs = (self.db.collection("receipts")
                .where("created_at", ">=", start_date)
                .where("created_at", "<=", end_date)
                .get())
        receipts = []
        for doc in docs:
            receipt_data = doc.to_dict()
            receipt_data["id"] = doc.id
            receipts.append(receipt_data)
        return receipts
