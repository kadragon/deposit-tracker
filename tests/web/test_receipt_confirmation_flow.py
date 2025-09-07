import pytest
from flask import Flask
from src.web.app import create_app
from unittest.mock import Mock, patch


def test_should_display_parsed_receipt_for_confirmation():
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    mock_store = Mock(id='store1', name='Test Store')
    mock_store_repo.get_by_id.return_value = mock_store
    
    # Mock users for the new functionality
    mock_users = []
    mock_user_repo.list_all.return_value = mock_users
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, ocr_service=mock_ocr_service,
                     store_repo=mock_store_repo)
    client = app.test_client()
    
    # Simulate confirming a parsed receipt
    response = client.get('/confirm-receipt?store_id=store1&total=5000&items=Item1:2000,Item2:3000')
    
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert 'receipt-confirmation' in response_text
    assert 'Test Store' in response_text
    assert '5000' in response_text


def test_should_allow_user_to_select_target_user():
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    mock_store = Mock(id='store1', name='Test Store')
    mock_store_repo.get_by_id.return_value = mock_store
    
    # Mock users for selection
    mock_users = [
        Mock(id='user1', name='User 1'),
        Mock(id='user2', name='User 2')
    ]
    mock_user_repo.list_all.return_value = mock_users
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, ocr_service=mock_ocr_service,
                     store_repo=mock_store_repo)
    client = app.test_client()
    
    response = client.get('/confirm-receipt?store_id=store1&total=5000')
    
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert 'user-selection' in response_text
    assert 'User 1' in response_text
    assert 'User 2' in response_text


def test_should_allow_user_to_choose_deposit_usage():
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    mock_store = Mock(id='store1', name='Test Store')
    mock_store_repo.get_by_id.return_value = mock_store
    
    # Mock empty users list
    mock_user_repo.list_all.return_value = []
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, ocr_service=mock_ocr_service,
                     store_repo=mock_store_repo)
    client = app.test_client()
    
    response = client.get('/confirm-receipt?store_id=store1&total=5000')
    
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert 'deposit-choice' in response_text


def test_should_process_confirmed_receipt():
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    mock_coupon_service = Mock()

    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, ocr_service=mock_ocr_service,
                     store_repo=mock_store_repo, coupon_service=mock_coupon_service)
    client = app.test_client()
    
    # Simulate POST to process the confirmed receipt
    response = client.post('/process-receipt', data={
        'user_id': 'user1',
        'store_id': 'store1',
        'total': '5000',
        'use_deposit': 'no'
    })
    
    assert response.status_code == 302  # Redirects
    assert 'success' in response.location
