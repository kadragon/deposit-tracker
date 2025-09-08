import os
from typing import Optional
from .receipt_parser_interface import ReceiptParserInterface
from .regex_receipt_parser import RegexReceiptParser
from .llm_receipt_parser import LLMReceiptParser
from .ocr_service import OCRService


class ReceiptParserFactory:
    """Factory for creating receipt parsers based on configuration"""
    
    @staticmethod
    def create_parser(
        use_llm: Optional[bool] = None,
        llm_model: str = "gpt-4o-mini",
        openai_api_key: Optional[str] = None
    ) -> ReceiptParserInterface:
        """Create a receipt parser based on configuration
        
        Args:
            use_llm: Whether to use LLM parser. If None, reads from LLM_PARSER_ENABLED env var
            llm_model: LLM model to use (default: gpt-4o-mini)
            openai_api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var
            
        Returns:
            ReceiptParserInterface implementation (LLM or regex-based)
        """
        # Determine parser type from parameter or environment
        if use_llm is None:
            use_llm = os.getenv("LLM_PARSER_ENABLED", "false").lower() == "true"
            
        # Check if we have OpenAI API key available
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Use LLM parser if explicitly requested and API key is available
        if use_llm and api_key:
            try:
                return LLMReceiptParser(api_key=api_key, model=llm_model)
            except Exception:
                # Fallback to regex parser if LLM initialization fails
                pass
                
        # Default to regex parser
        return RegexReceiptParser(OCRService())
    
    @staticmethod
    def create_llm_parser(
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini"
    ) -> LLMReceiptParser:
        """Create an LLM parser directly
        
        Args:
            api_key: OpenAI API key
            model: LLM model to use
            
        Returns:
            LLMReceiptParser instance
        """
        return LLMReceiptParser(api_key=api_key, model=model)
    
    @staticmethod
    def create_regex_parser(ocr_service: Optional[OCRService] = None) -> RegexReceiptParser:
        """Create a regex parser directly
        
        Args:
            ocr_service: OCR service instance (optional)
            
        Returns:
            RegexReceiptParser instance
        """
        return RegexReceiptParser(ocr_service)
    
    @staticmethod
    def create_fallback_parser(
        primary_parser: ReceiptParserInterface,
        fallback_parser: ReceiptParserInterface
    ) -> 'FallbackReceiptParser':
        """Create a parser that tries primary parser first, then falls back
        
        Args:
            primary_parser: Parser to try first (e.g., LLM parser)
            fallback_parser: Parser to use if primary fails (e.g., regex parser)
            
        Returns:
            FallbackReceiptParser instance
        """
        return FallbackReceiptParser(primary_parser, fallback_parser)


class FallbackReceiptParser(ReceiptParserInterface):
    """Parser that tries primary parser first, then falls back to secondary"""
    
    def __init__(self, primary: ReceiptParserInterface, fallback: ReceiptParserInterface):
        self.primary = primary
        self.fallback = fallback
    
    def parse(self, ocr_text: str):
        """Try primary parser first, fallback on empty results"""
        try:
            result = self.primary.parse(ocr_text)
            # If primary parser returns empty results, use fallback
            if (not result.store_name and 
                not result.date and 
                not result.items):
                return self.fallback.parse(ocr_text)
            return result
        except Exception:
            # On any error with primary parser, use fallback
            return self.fallback.parse(ocr_text)
    
    def parse_store_name(self, ocr_text: str) -> Optional[str]:
        """Try primary parser first, fallback on None/empty result"""
        try:
            result = self.primary.parse_store_name(ocr_text)
            if result is None or result.strip() == "":
                return self.fallback.parse_store_name(ocr_text)
            return result
        except Exception:
            return self.fallback.parse_store_name(ocr_text)
    
    def parse_items_and_prices(self, ocr_text: str):
        """Try primary parser first, fallback on empty result"""
        try:
            result = self.primary.parse_items_and_prices(ocr_text)
            if not result:
                return self.fallback.parse_items_and_prices(ocr_text)
            return result
        except Exception:
            return self.fallback.parse_items_and_prices(ocr_text)
    
    def parse_date(self, ocr_text: str) -> Optional[str]:
        """Try primary parser first, fallback on None/empty result"""
        try:
            result = self.primary.parse_date(ocr_text)
            if result is None or result.strip() == "":
                return self.fallback.parse_date(ocr_text)
            return result
        except Exception:
            return self.fallback.parse_date(ocr_text)