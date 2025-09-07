import pytest
from flask import Flask
from src.web.app import app
from unittest.mock import Mock, patch


def test_should_display_receipt_upload_form():
    client = app.test_client()
    response = client.get('/upload')
    
    assert response.status_code == 200
    assert 'upload-form' in response.get_data(as_text=True)


def test_should_handle_image_upload():
    from io import BytesIO
    
    with patch('src.web.app.OCRService') as mock_ocr_service_class:
        mock_ocr_service = Mock()
        mock_ocr_service_class.return_value = mock_ocr_service
        mock_ocr_service.extract_text_from_image.return_value = "Test text"
        mock_ocr_service.parse_store_name.return_value = "Test Store"
        mock_ocr_service.parse_items_and_prices.return_value = []
        
        client = app.test_client()
        data = {'file': (BytesIO(b'fake image'), 'test.jpg')}
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        assert 'image-uploaded' in response.get_data(as_text=True)


def test_should_display_ocr_results_for_confirmation():
    from io import BytesIO
    
    with patch('src.web.app.OCRService') as mock_ocr_service_class, \
         patch('src.web.app.ReceiptParser') as mock_parser_class:
        mock_ocr_service = Mock()
        mock_ocr_service_class.return_value = mock_ocr_service
        mock_ocr_service.extract_text_from_image.return_value = "Test Store\n10,000원"
        mock_ocr_service.parse_store_name.return_value = "Test Store"
        mock_ocr_service.parse_items_and_prices.return_value = [("Test Item", 10000)]
        
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        
        client = app.test_client()
        data = {'file': (BytesIO(b'fake image'), 'test.jpg')}
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert "Test Store" in response_text
        assert "10000" in response_text