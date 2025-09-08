from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ParsedReceiptDTO:
    """Data Transfer Object for parsed receipt data"""
    store_name: Optional[str]
    date: Optional[str]
    items: List[Dict[str, any]]  # List of {"name": str, "price": int, "quantity": int}
    
    
class ReceiptParserInterface(ABC):
    """Interface for receipt parsers (regex-based and LLM-based)"""
    
    @abstractmethod
    def parse(self, ocr_text: str) -> ParsedReceiptDTO:
        """Parse OCR text and return structured receipt data
        
        Args:
            ocr_text: Raw OCR text from receipt
            
        Returns:
            ParsedReceiptDTO with parsed store name, date, and items
        """
        pass
    
    @abstractmethod
    def parse_store_name(self, ocr_text: str) -> Optional[str]:
        """Extract store name from OCR text"""
        pass
        
    @abstractmethod  
    def parse_items_and_prices(self, ocr_text: str) -> List[Dict[str, int]]:
        """Extract items and prices from OCR text"""
        pass
        
    @abstractmethod
    def parse_date(self, ocr_text: str) -> Optional[str]:
        """Extract date from OCR text"""
        pass