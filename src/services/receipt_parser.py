from typing import TYPE_CHECKING, Optional
from src.models.store import Store
from src.models.receipt import Receipt
from src.services.receipt_parser_factory import ReceiptParserFactory

if TYPE_CHECKING:
    from src.services.ocr_service import OCRService
    from src.services.receipt_parser_interface import ReceiptParserInterface
    from src.models.user import User


class ReceiptParser:
    def __init__(self, ocr_service: Optional["OCRService"] = None, parser: Optional["ReceiptParserInterface"] = None):
        """Initialize receipt parser with either OCR service or parser interface
        
        Args:
            ocr_service: Legacy OCR service (for backward compatibility)
            parser: New parser interface (LLM or regex-based)
        """
        if parser is not None:
            self.parser = parser
        elif ocr_service is not None:
            # Legacy compatibility - wrap OCR service in regex parser
            from src.services.regex_receipt_parser import RegexReceiptParser
            self.parser = RegexReceiptParser(ocr_service)
        else:
            # Use factory to create appropriate parser based on environment
            self.parser = ReceiptParserFactory.create_parser()
            
        # Keep reference to OCR service for backward compatibility
        self.ocr_service = getattr(self.parser, 'ocr_service', None)

    def create_receipt_from_ocr_result(self, user: "User", ocr_text: str) -> Receipt:
        # Parse using the new interface
        parsed_data = self.parser.parse(ocr_text)
        
        # Parse store name
        store_name = parsed_data.store_name
        if store_name is None:
            store_name = "알 수 없는 매장"
        store = Store(name=store_name)

        # Parse date for actual purchase date
        purchase_date = parsed_data.date

        # Create receipt with purchase date
        receipt = Receipt(user=user, store=store, purchase_date=purchase_date)

        # Parse and add items
        items = parsed_data.items
        for item in items:
            quantity = item.get("quantity", 1)  # default quantity 1
            receipt.add_item(item["name"], item["price"], quantity)

        return receipt
