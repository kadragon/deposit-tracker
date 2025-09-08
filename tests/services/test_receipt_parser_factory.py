import pytest
from unittest.mock import Mock, patch
from src.services.receipt_parser_factory import ReceiptParserFactory, FallbackReceiptParser
from src.services.regex_receipt_parser import RegexReceiptParser
from src.services.llm_receipt_parser import LLMReceiptParser
from src.services.receipt_parser_interface import ParsedReceiptDTO


@patch('src.services.receipt_parser_factory.os.getenv')
def test_should_create_regex_parser_by_default(mock_getenv):
    # Given - LLM is disabled by default
    mock_getenv.side_effect = lambda key, default=None: {
        "LLM_PARSER_ENABLED": "false",
        "OPENAI_API_KEY": None
    }.get(key, default)
    
    # When
    parser = ReceiptParserFactory.create_parser()
    
    # Then
    assert isinstance(parser, RegexReceiptParser)


@patch('src.services.receipt_parser_factory.os.getenv')
@patch('src.services.llm_receipt_parser.OpenAI')
def test_should_create_llm_parser_when_enabled_and_key_available(mock_openai, mock_getenv):
    # Given - LLM is enabled and API key is available
    mock_getenv.side_effect = lambda key, default=None: {
        "LLM_PARSER_ENABLED": "true", 
        "OPENAI_API_KEY": "test-key"
    }.get(key, default)
    
    mock_client = Mock()
    mock_openai.return_value = mock_client
    
    # When
    parser = ReceiptParserFactory.create_parser()
    
    # Then
    assert isinstance(parser, LLMReceiptParser)


@patch('src.services.receipt_parser_factory.os.getenv')
def test_should_fallback_to_regex_when_llm_enabled_but_no_key(mock_getenv):
    # Given - LLM is enabled but no API key
    mock_getenv.side_effect = lambda key, default=None: {
        "LLM_PARSER_ENABLED": "true",
        "OPENAI_API_KEY": None
    }.get(key, default)
    
    # When
    parser = ReceiptParserFactory.create_parser()
    
    # Then - Should fallback to regex parser
    assert isinstance(parser, RegexReceiptParser)


@patch('src.services.llm_receipt_parser.OpenAI')
def test_should_create_llm_parser_explicitly(mock_openai):
    # Given
    mock_client = Mock()
    mock_openai.return_value = mock_client
    
    # When
    parser = ReceiptParserFactory.create_llm_parser(api_key="test-key")
    
    # Then
    assert isinstance(parser, LLMReceiptParser)


def test_should_create_regex_parser_explicitly():
    # When
    parser = ReceiptParserFactory.create_regex_parser()
    
    # Then
    assert isinstance(parser, RegexReceiptParser)


@patch('src.services.llm_receipt_parser.OpenAI')
def test_should_create_fallback_parser(mock_openai):
    # Given
    mock_client = Mock()
    mock_openai.return_value = mock_client
    
    primary = ReceiptParserFactory.create_llm_parser(api_key="test-key")
    fallback = ReceiptParserFactory.create_regex_parser()
    
    # When
    parser = ReceiptParserFactory.create_fallback_parser(primary, fallback)
    
    # Then
    assert isinstance(parser, FallbackReceiptParser)
    assert parser.primary == primary
    assert parser.fallback == fallback


@patch('src.services.llm_receipt_parser.OpenAI')
def test_fallback_parser_should_use_fallback_on_empty_result(mock_openai):
    # Given
    mock_client = Mock()
    mock_openai.return_value = mock_client
    
    # Create mocks for parsers
    primary_mock = Mock()
    primary_mock.parse.return_value = ParsedReceiptDTO(
        store_name=None, 
        date=None, 
        items=[]
    )
    
    fallback_mock = Mock()
    fallback_mock.parse.return_value = ParsedReceiptDTO(
        store_name="이마트", 
        date="2024-09-08 12:00:00",
        items=[{"name": "사과", "price": 2000, "quantity": 1}]
    )
    
    parser = FallbackReceiptParser(primary_mock, fallback_mock)
    
    # When - primary returns empty result
    result = parser.parse("test ocr text")
    
    # Then - should use fallback result
    assert result.store_name == "이마트"
    assert result.date == "2024-09-08 12:00:00"
    assert len(result.items) == 1
    assert result.items[0]["name"] == "사과"


@patch('src.services.llm_receipt_parser.OpenAI')
def test_fallback_parser_should_use_fallback_on_exception(mock_openai):
    # Given
    mock_client = Mock()
    mock_openai.return_value = mock_client
    
    # Create mocks for parsers
    primary_mock = Mock()
    primary_mock.parse.side_effect = Exception("API Error")
    
    fallback_mock = Mock()
    fallback_mock.parse.return_value = ParsedReceiptDTO(
        store_name="스타벅스", 
        date="2024-09-08 10:00:00",
        items=[{"name": "아메리카노", "price": 4500, "quantity": 1}]
    )
    
    parser = FallbackReceiptParser(primary_mock, fallback_mock)
    
    # When - primary throws exception
    result = parser.parse("test ocr text")
    
    # Then - should use fallback result
    assert result.store_name == "스타벅스"
    assert result.date == "2024-09-08 10:00:00"
    assert len(result.items) == 1
    assert result.items[0]["name"] == "아메리카노"


@patch('src.services.llm_receipt_parser.OpenAI')
def test_fallback_parser_should_use_primary_when_successful(mock_openai):
    # Given
    mock_client = Mock()
    mock_openai.return_value = mock_client
    
    # Create mocks for parsers
    primary_mock = Mock()
    primary_mock.parse.return_value = ParsedReceiptDTO(
        store_name="카페베네", 
        date="2024-09-08 14:00:00",
        items=[{"name": "라떼", "price": 5000, "quantity": 1}]
    )
    
    fallback_mock = Mock()
    # fallback should not be called
    
    parser = FallbackReceiptParser(primary_mock, fallback_mock)
    
    # When - primary returns valid result
    result = parser.parse("test ocr text")
    
    # Then - should use primary result
    assert result.store_name == "카페베네"
    assert result.date == "2024-09-08 14:00:00"
    assert len(result.items) == 1
    assert result.items[0]["name"] == "라떼"
    
    # Verify fallback was not called
    fallback_mock.parse.assert_not_called()