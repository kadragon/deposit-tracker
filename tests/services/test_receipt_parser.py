import pytest
from unittest.mock import Mock, patch
from src.services.receipt_parser import ReceiptParser
from src.services.ocr_service import OCRService
from src.services.receipt_parser_interface import ParsedReceiptDTO
from src.models.user import User
from src.models.store import Store
from src.models.receipt import Receipt


def test_should_create_receipt_from_ocr_result():
    # Given
    ocr_service_mock = Mock(spec=OCRService)
    receipt_parser = ReceiptParser(ocr_service_mock)
    
    user = User(name="홍길동", deposit=50000)
    ocr_text = """
    이마트 구로점
    서울특별시 구로구 구로동
    TEL: 02-1234-5678
    일시: 2024-01-15 14:30:22
    사과 2,000원
    바나나 3,000원
    우유 1,500원
    총계: 6,500원
    """
    
    # Mock the OCR service calls
    ocr_service_mock.parse_store_name.return_value = "이마트 구로점"
    ocr_service_mock.parse_items_and_prices.return_value = [
        {"name": "사과", "price": 2000},
        {"name": "바나나", "price": 3000},
        {"name": "우유", "price": 1500}
    ]
    ocr_service_mock.parse_date.return_value = "2024-01-15 14:30:22"
    
    # When
    receipt = receipt_parser.create_receipt_from_ocr_result(user, ocr_text)
    
    # Then
    assert receipt is not None
    assert receipt.user == user
    assert receipt.store.name == "이마트 구로점"
    assert len(receipt.items) == 3
    assert receipt.calculate_total() == 6500
    
    # Verify OCR service was called correctly
    ocr_service_mock.parse_store_name.assert_called_once_with(ocr_text)
    ocr_service_mock.parse_items_and_prices.assert_called_once_with(ocr_text)
    ocr_service_mock.parse_date.assert_called_once_with(ocr_text)


def test_should_handle_missing_store_in_ocr():
    # Given
    ocr_service_mock = Mock(spec=OCRService)
    receipt_parser = ReceiptParser(ocr_service_mock)
    
    user = User(name="홍길동", deposit=50000)
    ocr_text = """
    서울특별시 구로구 구로동
    TEL: 02-1234-5678
    일시: 2024-01-15 14:30:22
    사과 2,000원
    바나나 3,000원
    총계: 5,000원
    """
    
    # Mock the OCR service calls - store name is None (missing)
    ocr_service_mock.parse_store_name.return_value = None
    ocr_service_mock.parse_items_and_prices.return_value = [
        {"name": "사과", "price": 2000},
        {"name": "바나나", "price": 3000}
    ]
    ocr_service_mock.parse_date.return_value = "2024-01-15 14:30:22"
    
    # When
    receipt = receipt_parser.create_receipt_from_ocr_result(user, ocr_text)
    
    # Then
    assert receipt is not None
    assert receipt.user == user
    assert receipt.store.name == "알 수 없는 매장"  # Default store name
    assert len(receipt.items) == 2


def test_should_handle_invalid_price_format():
    # Given
    ocr_service_mock = Mock(spec=OCRService)
    receipt_parser = ReceiptParser(ocr_service_mock)
    
    user = User(name="홍길동", deposit=50000)
    ocr_text = """
    이마트 구로점
    서울특별시 구로구 구로동  
    TEL: 02-1234-5678
    사과 잘못된가격원
    바나나 3,000원
    총계: 알수없음원
    """
    
    # Mock the OCR service calls - items parsing returns empty due to invalid format
    ocr_service_mock.parse_store_name.return_value = "이마트 구로점"
    ocr_service_mock.parse_items_and_prices.return_value = [
        {"name": "바나나", "price": 3000}  # Only valid item
    ]
    ocr_service_mock.parse_date.return_value = None
    
    # When
    receipt = receipt_parser.create_receipt_from_ocr_result(user, ocr_text)
    
    # Then
    assert receipt is not None
    assert receipt.user == user
    assert receipt.store.name == "이마트 구로점"
    assert len(receipt.items) == 1  # Only one valid item parsed
    assert receipt.calculate_total() == 3000


def test_should_create_receipt_items_ready_for_assignment():
    # Given
    ocr_service_mock = Mock(spec=OCRService)
    receipt_parser = ReceiptParser(ocr_service_mock)
    
    user = User(name="홍길동", deposit=50000)
    ocr_text = """
    스타벅스 강남점
    서울특별시 강남구
    TEL: 02-1234-5678
    일시: 2024-01-15 10:30:00
    아메리카노 4,500원
    치즈케이크 6,200원  
    라떼 5,000원
    총계: 15,700원
    """
    
    # Mock the OCR service calls
    ocr_service_mock.parse_store_name.return_value = "스타벅스 강남점"
    ocr_service_mock.parse_items_and_prices.return_value = [
        {"name": "아메리카노", "price": 4500},
        {"name": "치즈케이크", "price": 6200},
        {"name": "라떼", "price": 5000}
    ]
    ocr_service_mock.parse_date.return_value = "2024-01-15 10:30:00"
    
    # When
    receipt = receipt_parser.create_receipt_from_ocr_result(user, ocr_text)
    
    # Then
    assert receipt is not None
    assert len(receipt.items) == 3
    
    # Verify each item is ready for assignment but has no users assigned initially
    for item in receipt.items:
        # Items should have assigned_users attribute (ready for assignment)
        assert hasattr(item, 'assigned_users')
        assert isinstance(item.assigned_users, list)
        
        # Items should start with no users assigned
        assert len(item.assigned_users) == 0
        
        # Items should support assignment functionality
        assert hasattr(item, 'assign_to_user')
        assert hasattr(item, 'is_shared')
        assert hasattr(item, 'calculate_per_user_amounts')
        
        # Verify initial state - not shared since no users assigned
        assert item.is_shared() == False
        assert item.calculate_per_user_amounts() == {}
    
    # Verify specific items and their prices
    americano = receipt.items[0]
    assert americano.name == "아메리카노"
    assert americano.price == 4500
    
    cheesecake = receipt.items[1] 
    assert cheesecake.name == "치즈케이크"
    assert cheesecake.price == 6200
    
    latte = receipt.items[2]
    assert latte.name == "라떼"
    assert latte.price == 5000
    
    # Test assignment functionality works
    americano.assign_to_user(user)
    assert len(americano.assigned_users) == 1
    assert americano.assigned_users[0] == user
    assert americano.is_shared() == False  # Still not shared (only 1 user)
    
    # Test per-user amount calculation
    user_amounts = americano.calculate_per_user_amounts()
    assert user_amounts[user] == 4500


def test_should_parse_items_with_llm_for_korean_receipt():
    # Given - Create a mock parser that mimics LLM parsing behavior
    mock_parser = Mock()
    mock_parser.parse.return_value = ParsedReceiptDTO(
        store_name="스타벅스 코엑스점",
        date="2024-09-08 12:34:56",
        items=[
            {"name": "아이스 아메리카노 (Tall)", "price": 4500, "quantity": 1},
            {"name": "카페라떼 (Grande)", "price": 5800, "quantity": 1}, 
            {"name": "초콜릿 케이크", "price": 6200, "quantity": 1},
            {"name": "쿠키", "price": 3000, "quantity": 1}
        ]
    )
    
    # Create ReceiptParser with the mocked parser (this simulates LLM parser usage)
    receipt_parser = ReceiptParser(parser=mock_parser)
    
    user = User(name="홍길동", deposit=50000)
    
    # Korean receipt OCR text with various formatting
    korean_ocr_text = """
    스타벅스 코엑스점
    서울특별시 강남구 영동대로 513
    TEL: 02-6002-8000
    
    2024/09/08(일) 12:34:56
    영수증 번호: 1234-5678
    
    * 주문 내역 *
    아이스 아메리카노 (Tall)    4,500원
    카페라떼 (Grande)          5,800원
    초콜릿 케이크               6,200원
    쿠키                       3,000원
    
    ---------------------------
    소계                      19,500원
    할인                      -1,000원
    ---------------------------
    총 결제금액                18,500원
    
    카드결제                  18,500원
    승인번호: 12345678
    """
    
    # When
    receipt = receipt_parser.create_receipt_from_ocr_result(user, korean_ocr_text)
    
    # Then
    assert receipt is not None
    assert receipt.store.name == "스타벅스 코엑스점"
    assert len(receipt.items) == 4
    
    # Verify LLM parsed items correctly (ignoring meta lines like 소계, 할인, 총계)
    items = receipt.items
    assert items[0].name == "아이스 아메리카노 (Tall)"
    assert items[0].price == 4500
    assert items[1].name == "카페라떼 (Grande)"
    assert items[1].price == 5800
    assert items[2].name == "초콜릿 케이크"
    assert items[2].price == 6200
    assert items[3].name == "쿠키"
    assert items[3].price == 3000
    
    # Should calculate correct total from items (not including discount)
    total_from_items = sum(item.calculate_total() for item in items)
    assert total_from_items == 19500  # Sum of individual items before discount
    
    # Verify the parser interface was called correctly
    mock_parser.parse.assert_called_once_with(korean_ocr_text)