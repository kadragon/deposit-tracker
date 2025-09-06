from google.cloud import firestore
from datetime import datetime


class ReceiptRepository:
    def __init__(self):
        self.db = firestore.Client()
    
    def save(self, receipt):
        receipt_data = {
            "user_id": receipt.user.id,
            "store_id": receipt.store.id,
            "items": [
                {
                    "name": item["name"],
                    "price": item["price"],
                    "quantity": item["quantity"]
                }
                for item in receipt.items
            ],
            "total": receipt.calculate_total(),
            "created_at": datetime.now()
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