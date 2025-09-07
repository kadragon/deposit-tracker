from typing import TYPE_CHECKING
from src.models.store import Store
from src.models.receipt import Receipt

if TYPE_CHECKING:
    from src.services.ocr_service import OCRService
    from src.models.user import User


class ReceiptParser:
    def __init__(self, ocr_service: "OCRService"):
        self.ocr_service = ocr_service

    def create_receipt_from_ocr_result(self, user: "User", ocr_text: str) -> Receipt:
        # Parse store name
        store_name = self.ocr_service.parse_store_name(ocr_text)
        if store_name is None:
            store_name = "알 수 없는 매장"
        store = Store(name=store_name)

        # Parse date for actual purchase date
        purchase_date = self.ocr_service.parse_date(ocr_text)

        # Create receipt with purchase date
        receipt = Receipt(user=user, store=store, purchase_date=purchase_date)

        # Parse and add items
        items = self.ocr_service.parse_items_and_prices(ocr_text)
        for item in items:
            receipt.add_item(item["name"], item["price"], 1)  # default quantity 1

        return receipt
