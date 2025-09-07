import pytest
from unittest.mock import Mock, patch
from src.services.ocr_service import OCRService
from unittest.mock import patch, Mock, mock_open


def test_should_extract_text_from_receipt_image():
    # Given: mock Vision API client
    ocr_service = OCRService()
    image_path = "/path/to/receipt.jpg"

    fake_annotation = Mock()
    fake_annotation.description = "이마트\n사과 2,000원\n총계: 2,000원"

    class FakeResponse:
        text_annotations = [fake_annotation]

    m = mock_open()
    m.return_value.read.return_value = b"dummy-image-bytes"
    with patch("builtins.open", m), \
         patch("google.cloud.vision.ImageAnnotatorClient") as mock_client_cls, \
         patch("google.cloud.vision.Image", wraps=lambda content=None: Mock()):
        mock_client = Mock()
        mock_client.text_detection.return_value = FakeResponse()
        mock_client_cls.return_value = mock_client

        # When
        extracted_text = ocr_service.extract_text(image_path)

    # Then
    assert extracted_text == "이마트\n사과 2,000원\n총계: 2,000원"


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


def test_should_parse_items_with_currency_and_spaces():
    # Given numbers with spaces and currency
    ocr_service = OCRService()
    ocr_text = """
    마트X
    서울특별시 강남구
    TEL: 02-0000-0000
    초콜릿   1 500원
    생수  1,  200원
    총계: 2,700원
    """

    # When
    items = ocr_service.parse_items_and_prices(ocr_text)

    # Then
    assert items == [
        {"name": "초콜릿", "price": 1500},
        {"name": "생수", "price": 1200},
    ]


def test_should_ignore_non_item_numeric_lines():
    ocr_service = OCRService()
    ocr_text = """
    카페Y
    TEL: 010-1234-5678
    영업시간 09:00-21:00
    총계: 0원
    """

    items = ocr_service.parse_items_and_prices(ocr_text)
    assert items == []


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
