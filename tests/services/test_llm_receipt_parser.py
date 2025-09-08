import pytest
from unittest.mock import Mock, patch
from src.services.llm_receipt_parser import LLMReceiptParser


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI response for testing"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = """{
  "store": "스타벅스 코엑스점",
  "date": "2024-09-08 12:34:56",
  "items": [
    {"name": "아이스 아메리카노 (Tall)", "price": 4500, "quantity": 1},
    {"name": "카페라떼 (Grande)", "price": 5800, "quantity": 1},
    {"name": "초콜릿 케이크", "price": 6200, "quantity": 1},
    {"name": "쿠키", "price": 3000, "quantity": 1}
  ]
}"""
    return mock_response


@patch('src.services.llm_receipt_parser.OpenAI')
def test_should_parse_items_with_llm_for_korean_receipt(mock_openai_client, mock_openai_response):
    # Given
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
    
    # Mock the OpenAI client
    mock_client_instance = Mock()
    mock_openai_client.return_value = mock_client_instance
    mock_client_instance.chat.completions.create.return_value = mock_openai_response
    
    parser = LLMReceiptParser(api_key="test-key")
    
    # When
    result = parser.parse_receipt(korean_ocr_text)
    
    # Then
    assert result["store"] == "스타벅스 코엑스점"
    assert result["date"] == "2024-09-08 12:34:56"
    assert len(result["items"]) == 4
    
    items = result["items"]
    assert items[0]["name"] == "아이스 아메리카노 (Tall)"
    assert items[0]["price"] == 4500
    assert items[1]["name"] == "카페라떼 (Grande)" 
    assert items[1]["price"] == 5800
    assert items[2]["name"] == "초콜릿 케이크"
    assert items[2]["price"] == 6200
    assert items[3]["name"] == "쿠키"
    assert items[3]["price"] == 3000


@patch('src.services.llm_receipt_parser.OpenAI')
def test_should_ignore_meta_lines_with_llm(mock_openai_client, mock_openai_response):
    # Given
    korean_ocr_text = """
    카페베네 홍대점
    TEL: 02-123-4567
    2024-09-08 15:20:30
    
    아메리카노              3,500원
    크로와상                4,500원
    
    소계                   8,000원
    부가세                   800원
    총계                   8,800원
    현금결제               8,800원
    """
    
    # Mock the OpenAI client
    mock_client_instance = Mock()
    mock_openai_client.return_value = mock_client_instance
    mock_client_instance.chat.completions.create.return_value = mock_openai_response
    
    parser = LLMReceiptParser(api_key="test-key")
    
    # When - LLM should ignore TEL, 소계, 부가세, 총계, 현금결제
    items = parser.parse_items_and_prices(korean_ocr_text)
    
    # Then - Only actual items should be returned
    assert len(items) == 4  # Based on mock response
    # Verify meta lines are not included in items
    item_names = [item["name"] for item in items]
    assert "TEL" not in " ".join(item_names)
    assert "소계" not in " ".join(item_names)
    assert "부가세" not in " ".join(item_names)
    assert "총계" not in " ".join(item_names)
    assert "현금결제" not in " ".join(item_names)


@patch('src.services.llm_receipt_parser.OpenAI')
def test_should_return_valid_json_schema_from_llm(mock_openai_client):
    # Given
    valid_json_response = Mock()
    valid_json_response.choices = [Mock()]
    valid_json_response.choices[0].message.content = """{
  "store": "이마트 구로점",
  "date": "2024-09-08 10:15:00", 
  "items": [
    {"name": "바나나", "price": 2500, "quantity": 1},
    {"name": "우유", "price": 3200, "quantity": 2}
  ]
}"""
    
    # Mock the OpenAI client
    mock_client_instance = Mock()
    mock_openai_client.return_value = mock_client_instance
    mock_client_instance.chat.completions.create.return_value = valid_json_response
    
    parser = LLMReceiptParser(api_key="test-key")
    
    # When
    result = parser.parse_receipt("test ocr text")
    
    # Then - Should return valid structured data
    assert isinstance(result, dict)
    assert "store" in result
    assert "date" in result  
    assert "items" in result
    assert isinstance(result["items"], list)
    
    # Verify item structure
    for item in result["items"]:
        assert "name" in item
        assert "price" in item
        assert "quantity" in item
        assert isinstance(item["price"], int)
        assert isinstance(item["quantity"], int)


@patch('src.services.llm_receipt_parser.OpenAI')
def test_should_handle_empty_llm_response(mock_openai_client):
    # Given
    empty_response = Mock()
    empty_response.choices = [Mock()]
    empty_response.choices[0].message.content = '{"store": null, "date": null, "items": []}'
    
    # Mock the OpenAI client
    mock_client_instance = Mock()
    mock_openai_client.return_value = mock_client_instance
    mock_client_instance.chat.completions.create.return_value = empty_response
    
    parser = LLMReceiptParser(api_key="test-key")
    
    # When LLM returns empty results
    result = parser.parse_receipt("invalid ocr text")
    
    # Then - Should return empty structure instead of None
    assert result["store"] is None
    assert result["date"] is None  
    assert result["items"] == []
        

@patch('src.services.llm_receipt_parser.OpenAI')
def test_should_extract_store_and_date_with_llm(mock_openai_client):
    # Given
    response_with_metadata = Mock()
    response_with_metadata.choices = [Mock()]
    response_with_metadata.choices[0].message.content = """{
  "store": "롯데마트 잠실점",
  "date": "2024-09-08 18:45:22",
  "items": [
    {"name": "사과", "price": 5000, "quantity": 1}
  ]
}"""
    
    # Mock the OpenAI client
    mock_client_instance = Mock()
    mock_openai_client.return_value = mock_client_instance
    mock_client_instance.chat.completions.create.return_value = response_with_metadata
    
    parser = LLMReceiptParser(api_key="test-key")
    ocr_text = "롯데마트 잠실점\n2024/09/08 18:45:22\n사과 5,000원"
    
    # When
    store_name = parser.parse_store_name(ocr_text)
    date = parser.parse_date(ocr_text)
    
    # Then
    assert store_name == "롯데마트 잠실점"
    assert date == "2024-09-08 18:45:22"


@patch('src.services.llm_receipt_parser.OpenAI')
def test_should_handle_api_errors_gracefully(mock_openai_client):
    # Given
    mock_client_instance = Mock()
    mock_openai_client.return_value = mock_client_instance
    mock_client_instance.chat.completions.create.side_effect = Exception("API Error")
    
    parser = LLMReceiptParser(api_key="test-key")
    
    # When API fails
    result = parser.parse_receipt("test text")
    
    # Then - Should return empty result instead of crashing
    assert result["store"] is None
    assert result["date"] is None
    assert result["items"] == []


@patch('src.services.llm_receipt_parser.OpenAI')
def test_should_handle_invalid_json_response(mock_openai_client):
    # Given  
    invalid_json_response = Mock()
    invalid_json_response.choices = [Mock()]
    invalid_json_response.choices[0].message.content = "Invalid JSON response from LLM"
    
    # Mock the OpenAI client
    mock_client_instance = Mock()
    mock_openai_client.return_value = mock_client_instance
    mock_client_instance.chat.completions.create.return_value = invalid_json_response
    
    parser = LLMReceiptParser(api_key="test-key")
    
    # When LLM returns invalid JSON
    result = parser.parse_receipt("test text")
    
    # Then - Should fallback to empty result
    assert result["store"] is None
    assert result["date"] is None
    assert result["items"] == []