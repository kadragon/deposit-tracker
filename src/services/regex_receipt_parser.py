from typing import List, Dict, Optional
from .receipt_parser_interface import ReceiptParserInterface, ParsedReceiptDTO
from .ocr_service import OCRService


class RegexReceiptParser(ReceiptParserInterface):
    """Regex-based receipt parser using the existing OCRService"""
    
    def __init__(self, ocr_service: OCRService = None):
        self.ocr_service = ocr_service or OCRService()
        
    def parse(self, ocr_text: str) -> ParsedReceiptDTO:
        """Parse OCR text using regex patterns"""
        store_name = self.parse_store_name(ocr_text)
        date = self.parse_date(ocr_text)
        items = self.parse_items_and_prices(ocr_text)
        
        return ParsedReceiptDTO(
            store_name=store_name,
            date=date,
            items=items
        )
    
    def parse_store_name(self, ocr_text: str) -> Optional[str]:
        """Extract store name using regex patterns"""
        return self.ocr_service.parse_store_name(ocr_text)
        
    def parse_items_and_prices(self, ocr_text: str) -> List[Dict[str, int]]:
        """Extract items and prices using regex patterns"""
        items = self.ocr_service.parse_items_and_prices(ocr_text)
        # Convert to expected format with quantity
        for item in items:
            if 'quantity' not in item:
                item['quantity'] = 1
        return items
        
    def parse_date(self, ocr_text: str) -> Optional[str]:
        """Extract date using regex patterns"""
        return self.ocr_service.parse_date(ocr_text)