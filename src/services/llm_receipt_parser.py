import json
import os
import time
from typing import List, Dict, Optional
from openai import OpenAI
from .receipt_parser_interface import ReceiptParserInterface, ParsedReceiptDTO


class LLMReceiptParser(ReceiptParserInterface):
    """LLM-based receipt parser using OpenAI GPT models for Korean receipt parsing."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """Initialize the LLM parser.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
            model: Model to use. Defaults to gpt-4o-mini.
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        
    def _make_api_call(self, system_prompt: str, user_content: str):
        """Make the actual API call to OpenAI. Separated for easier mocking."""
        return self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0,
            max_tokens=500
        )
    
    def parse(self, ocr_text: str) -> ParsedReceiptDTO:
        """Parse OCR text using LLM and return structured DTO"""
        result = self.parse_receipt(ocr_text)
        return ParsedReceiptDTO(
            store_name=result.get("store"),
            date=result.get("date"),
            items=result.get("items", [])
        )
        
    def parse_receipt(self, ocr_text: str) -> Dict:
        """Parse OCR text using LLM to extract structured receipt data.
        
        Args:
            ocr_text: Raw OCR text from receipt
            
        Returns:
            Dict with parsed receipt data containing store, date, and items
        """
        system_prompt = """You are a Korean receipt parser. Your job is to extract structured data from Korean receipt OCR text.

Extract the following information and return it as valid JSON:
- store: Store name (string or null if not found)  
- date: Date and time in "YYYY-MM-DD HH:MM:SS" format (string or null if not found)
- items: Array of items with name, price (in Korean won as integer), and quantity (integer)

Rules:
1. Only extract actual purchasable items (food, drinks, products)
2. Skip meta lines like: 총계, 소계, 할인, 부가세, 카드결제, 현금, TEL, 전화번호, 승인번호, 영수증번호
3. Remove commas from prices and convert to integers
4. If quantity is not specified, default to 1
5. Return valid JSON only, no additional text

Example output:
{
  "store": "스타벅스 강남점",
  "date": "2024-09-01 12:34:56", 
  "items": [
    {"name": "아메리카노", "price": 4500, "quantity": 1},
    {"name": "치즈케이크", "price": 6200, "quantity": 1}
  ]
}"""

        try:
            response = self._make_api_call(system_prompt, ocr_text)
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # Try to extract JSON from response if there's extra text
                try:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start != -1 and end > start:
                        json_str = content[start:end]
                        result = json.loads(json_str)
                        return result
                except json.JSONDecodeError:
                    pass
                    
                # If JSON parsing fails, return empty result
                return {"store": None, "date": None, "items": []}
                
        except Exception:
            # On any error, return empty result
            return {"store": None, "date": None, "items": []}
    
    def parse_store_name(self, ocr_text: str) -> Optional[str]:
        """Extract store name from OCR text using LLM."""
        result = self.parse_receipt(ocr_text)
        return result.get("store")
        
    def parse_items_and_prices(self, ocr_text: str) -> List[Dict[str, int]]:
        """Extract items and prices from OCR text using LLM."""
        result = self.parse_receipt(ocr_text)
        items = result.get("items", [])
        
        # Convert to format expected by existing code
        formatted_items = []
        for item in items:
            formatted_items.append({
                "name": item.get("name", ""),
                "price": item.get("price", 0),
                "quantity": item.get("quantity", 1)
            })
        
        return formatted_items
        
    def parse_date(self, ocr_text: str) -> Optional[str]:
        """Extract date from OCR text using LLM."""
        result = self.parse_receipt(ocr_text)
        return result.get("date")