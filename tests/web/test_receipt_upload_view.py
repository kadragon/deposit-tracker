import pytest
from flask import Flask
from src.web.app import create_app
from unittest.mock import Mock


def test_should_display_receipt_upload_form():
    # Create mock dependencies to avoid requiring real Google Cloud credentials
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    
    mock_store_repo = Mock()
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, ocr_service=mock_ocr_service,
                     store_repo=mock_store_repo)
    client = app.test_client()
    response = client.get('/upload')
    
    assert response.status_code == 200
    assert 'upload-form' in response.get_data(as_text=True)


def test_should_handle_image_upload():
    from io import BytesIO
    
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_ocr_service.extract_text_from_image.return_value = "Test text"
    mock_ocr_service.parse_store_name.return_value = "Test Store"
    mock_ocr_service.parse_items_and_prices.return_value = []
    mock_store_repo = Mock()
    mock_store = Mock(id='store1', name='Test Store')
    mock_store_repo.find_by_name.return_value = mock_store
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, ocr_service=mock_ocr_service,
                     store_repo=mock_store_repo)
    client = app.test_client()
    data = {'file': (BytesIO(b'fake image'), 'test.jpg')}
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 302
    assert '/confirm-receipt' in response.location
    assert 'store_id=store1' in response.location


def test_should_display_ocr_results_for_confirmation():
    from io import BytesIO
    
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_ocr_service.extract_text_from_image.return_value = "Test Store\n10,000원"
    mock_ocr_service.parse_store_name.return_value = "Test Store"
    mock_ocr_service.parse_items_and_prices.return_value = [{"name": "Test Item", "price": 10000}]
    mock_store_repo = Mock()
    mock_store = Mock(id='store1', name='Test Store')
    mock_store_repo.find_by_name.return_value = mock_store
    mock_store_repo.get_by_id.return_value = mock_store
    mock_user_repo.list_all.return_value = []
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, ocr_service=mock_ocr_service,
                     store_repo=mock_store_repo)
    client = app.test_client()
    data = {'file': (BytesIO(b'fake image'), 'test.jpg')}
    response = client.post('/upload', data=data, content_type='multipart/form-data')

    assert response.status_code == 302
    assert '/confirm-receipt' in response.location
    # Follow redirect to confirmation page
    confirm_response = client.get(response.location)
    assert confirm_response.status_code == 200
    text = confirm_response.get_data(as_text=True)
    assert 'receipt-confirmation' in text
    assert 'Test Store' in text
    assert '10000' in text
