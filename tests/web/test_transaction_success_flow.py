import pytest
from flask import Flask
from src.web.app import create_app
from unittest.mock import Mock, patch


def test_should_update_user_deposit_after_transaction():
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    
    # Mock user with deposit
    mock_user = Mock(id='user1', name='User 1', deposit=10000)
    mock_user_repo.get_by_id.return_value = mock_user
    
    # Mock dependencies
    with patch('src.web.app.CouponService') as mock_coupon_service_class, \
         patch('src.web.app.StoreRepository') as mock_store_repo_class:
        
        mock_coupon_service = Mock()
        mock_coupon_service_class.return_value = mock_coupon_service
        
        mock_store_repo = Mock()
        mock_store_repo_class.return_value = mock_store_repo
        
        app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                         coupon_repo=mock_coupon_repo, ocr_service=mock_ocr_service)
        client = app.test_client()
        
        # Process transaction with deposit
        response = client.post('/process-receipt', data={
            'user_id': 'user1',
            'store_name': 'Test Store',
            'total': '5000',
            'use_deposit': 'yes'
        })
        
        assert response.status_code == 302  # Now redirects
        # Verify user's subtract_deposit was called
        mock_user.subtract_deposit.assert_called_once_with(5000)
        mock_user_repo.save.assert_called_once_with(mock_user)


def test_should_award_coupon_after_transaction():
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    
    # Mock user
    mock_user = Mock(id='user1', name='User 1')
    mock_user_repo.get_by_id.return_value = mock_user
    
    # Mock coupon service and store repository  
    with patch('src.web.app.CouponService') as mock_coupon_service_class, \
         patch('src.web.app.StoreRepository') as mock_store_repo_class:
        
        mock_coupon_service = Mock()
        mock_coupon_service_class.return_value = mock_coupon_service
        
        mock_store_repo = Mock()
        mock_store_repo_class.return_value = mock_store_repo
        
        app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                         coupon_repo=mock_coupon_repo, ocr_service=mock_ocr_service)
        client = app.test_client()
        
        # Process transaction
        response = client.post('/process-receipt', data={
            'user_id': 'user1',
            'store_name': 'Test Store',
            'total': '5000',
            'use_deposit': 'no'
        })
        
        assert response.status_code == 302  # Now redirects
        # Verify coupon service was called
        mock_coupon_service.award_coupon.assert_called_once_with('user1', 'Test Store')


def test_should_redirect_to_success_page():
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    
    # Mock dependencies
    with patch('src.web.app.CouponService') as mock_coupon_service_class, \
         patch('src.web.app.StoreRepository') as mock_store_repo_class:
        
        mock_coupon_service = Mock()
        mock_coupon_service_class.return_value = mock_coupon_service
        
        mock_store_repo = Mock()
        mock_store_repo_class.return_value = mock_store_repo
        
        app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                         coupon_repo=mock_coupon_repo, ocr_service=mock_ocr_service)
        client = app.test_client()
        
        # Process transaction
        response = client.post('/process-receipt', data={
            'user_id': 'user1',
            'store_name': 'Test Store',
            'total': '5000',
            'use_deposit': 'no'
        })
        
        assert response.status_code == 302  # Redirect status
        assert 'success' in response.location