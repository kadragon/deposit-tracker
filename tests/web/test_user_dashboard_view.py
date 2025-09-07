import pytest
from flask import Flask
from src.web.app import app
from unittest.mock import Mock, patch


def test_should_display_user_deposit_balance():
    with patch('src.web.app.UserRepository') as mock_user_repo_class, \
         patch('src.web.app.ReceiptRepository') as mock_receipt_repo_class, \
         patch('src.web.app.CouponRepository') as mock_coupon_repo_class:
        mock_user_repo = Mock()
        mock_user_repo_class.return_value = mock_user_repo
        mock_user = Mock(name="홍길동", deposit=25000)
        mock_user_repo.get_by_id.return_value = mock_user
        
        mock_receipt_repo = Mock()
        mock_receipt_repo_class.return_value = mock_receipt_repo
        mock_receipt_repo.get_by_user_id.return_value = []
        
        mock_coupon_repo = Mock()
        mock_coupon_repo_class.return_value = mock_coupon_repo
        mock_coupon_repo.get_by_user_id.return_value = []
        
        client = app.test_client()
        response = client.get('/dashboard/user123')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert "홍길동" in response_text
        assert "25000" in response_text


def test_should_display_recent_transactions():
    with patch('src.web.app.UserRepository') as mock_user_repo_class, \
         patch('src.web.app.ReceiptRepository') as mock_receipt_repo_class, \
         patch('src.web.app.CouponRepository') as mock_coupon_repo_class:
        mock_user_repo = Mock()
        mock_user_repo_class.return_value = mock_user_repo
        mock_user = Mock(name="홍길동", deposit=25000)
        mock_user_repo.get_by_id.return_value = mock_user
        
        mock_receipt_repo = Mock()
        mock_receipt_repo_class.return_value = mock_receipt_repo
        mock_receipt = Mock(store_name="테스트 매장", total_amount=15000)
        mock_receipt_repo.get_by_user_id.return_value = [mock_receipt]
        
        mock_coupon_repo = Mock()
        mock_coupon_repo_class.return_value = mock_coupon_repo
        mock_coupon_repo.get_by_user_id.return_value = []
        
        client = app.test_client()
        response = client.get('/dashboard/user123')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert "테스트 매장" in response_text
        assert "15000" in response_text


def test_should_display_coupon_progress():
    with patch('src.web.app.UserRepository') as mock_user_repo_class, \
         patch('src.web.app.ReceiptRepository') as mock_receipt_repo_class, \
         patch('src.web.app.CouponRepository') as mock_coupon_repo_class:
        mock_user_repo = Mock()
        mock_user_repo_class.return_value = mock_user_repo
        mock_user = Mock(name="홍길동", deposit=25000)
        mock_user_repo.get_by_id.return_value = mock_user
        
        mock_receipt_repo = Mock()
        mock_receipt_repo_class.return_value = mock_receipt_repo
        mock_receipt_repo.get_by_user_id.return_value = []
        
        mock_coupon_repo = Mock()
        mock_coupon_repo_class.return_value = mock_coupon_repo
        mock_coupon = Mock(store_name="테스트 매장", count=3, goal=5)
        mock_coupon_repo.get_by_user_id.return_value = [mock_coupon]
        
        client = app.test_client()
        response = client.get('/dashboard/user123')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert "테스트 매장" in response_text
        assert "3" in response_text
        assert "5" in response_text