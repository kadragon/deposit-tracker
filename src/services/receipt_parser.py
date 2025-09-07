from src.models.store import Store
from src.models.receipt import Receipt


class ReceiptParser:
    def __init__(self, ocr_service):
        self.ocr_service = ocr_service
    
    def create_receipt_from_ocr_result(self, user, ocr_text):
        # Parse store name
        store_name = self.ocr_service.parse_store_name(ocr_text)
        if store_name is None:
            store_name = "알 수 없는 매장"
        store = Store(name=store_name)
        
        # Create receipt
        receipt = Receipt(user=user, store=store)
        
        # Parse and add items
        items = self.ocr_service.parse_items_and_prices(ocr_text)
        for item in items:
            receipt.add_item(item["name"], item["price"], 1)  # default quantity 1
        
        # Parse date (for future use)
        date = self.ocr_service.parse_date(ocr_text)
        
        return receipt