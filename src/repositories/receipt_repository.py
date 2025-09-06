from typing import Any, List, Optional
from decimal import Decimal
from google.cloud import firestore


class ReceiptRepository:
    def __init__(self, client: Optional[firestore.Client] = None):
        # Allow dependency injection for easier testing and configurability
        self.db = client or firestore.Client()
    
    def save(self, receipt: Any) -> str:
        def _serialize_item(item: Any) -> dict:
            if isinstance(item, dict):
                return {
                    "name": item["name"],
                    # Ensure Firestore stores JSON-serializable numeric types
                    "price": int(item["price"]) if isinstance(item["price"], Decimal) else item["price"],
                    "quantity": int(item["quantity"]),
                }
            # Fallback for ReceiptItem-like objects
            return {
                "name": getattr(item, "name"),
                "price": int(getattr(item, "price")) if isinstance(getattr(item, "price"), Decimal) else getattr(item, "price"),
                "quantity": int(getattr(item, "quantity", 1)),
            }

        receipt_data = {
            "user_id": getattr(receipt.user, "id", None),
            "store_id": getattr(receipt.store, "id", None),
            "items": [_serialize_item(item) for item in receipt.items],
            "total": int(receipt.calculate_total()) if isinstance(receipt.calculate_total(), Decimal) else receipt.calculate_total(),
            # Prefer server timestamp for consistency across environments
            "created_at": firestore.SERVER_TIMESTAMP,
        }

        doc_ref, _ = self.db.collection("receipts").add(receipt_data)
        return doc_ref.id
    
    def find_by_user_id(self, user_id):
        docs = self.db.collection("receipts").where("user_id", "==", user_id).get()
        receipts = []
        for doc in docs:
            receipt_data = doc.to_dict()
            receipt_data["id"] = doc.id
            receipts.append(receipt_data)
        return receipts
    
    def find_by_date_range(self, start_date, end_date):
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
