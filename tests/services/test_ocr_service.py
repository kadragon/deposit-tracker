import pytest
from unittest.mock import Mock, patch
from src.services.ocr_service import OCRService


def test_should_extract_text_from_receipt_image():
    # Given
    ocr_service = OCRService()
    image_path = "/path/to/receipt.jpg"
    
    # When
    extracted_text = ocr_service.extract_text(image_path)
    
    # Then
    assert extracted_text is not None
    assert isinstance(extracted_text, str)
    assert len(extracted_text) > 0


def test_should_parse_store_name_from_ocr_text():
    # Given
    ocr_service = OCRService()
    ocr_text = """
    이마트 구로점
    서울특별시 구로구 구로동
    TEL: 02-1234-5678
    사과 2,000원
    바나나 3,000원
    총계: 5,000원
    """
    
    # When
    store_name = ocr_service.parse_store_name(ocr_text)
    
    # Then
    assert store_name == "이마트 구로점"


def test_should_parse_items_and_prices_from_ocr_text():
    # Given
    ocr_service = OCRService()
    ocr_text = """
    이마트 구로점
    서울특별시 구로구 구로동
    TEL: 02-1234-5678
    사과 2,000원
    바나나 3,000원
    우유 1,500원
    총계: 6,500원
    """
    
    # When
    items = ocr_service.parse_items_and_prices(ocr_text)
    
    # Then
    expected_items = [
        {"name": "사과", "price": 2000},
        {"name": "바나나", "price": 3000},
        {"name": "우유", "price": 1500}
    ]
    assert items == expected_items


def test_should_parse_date_from_ocr_text():
    # Given
    ocr_service = OCRService()
    ocr_text = """
    이마트 구로점
    서울특별시 구로구 구로동
    TEL: 02-1234-5678
    일시: 2024-01-15 14:30:22
    사과 2,000원
    바나나 3,000원
    총계: 5,000원
    """
    
    # When
    date = ocr_service.parse_date(ocr_text)
    
    # Then
    assert date == "2024-01-15 14:30:22"