import pytest
from flask import Flask
from src.web.app import create_app
from unittest.mock import Mock, patch


def test_should_display_user_deposit_balance():
    mock_user_repo = Mock()
    mock_user = Mock(name="홍길동", deposit=25000)
    mock_user_repo.get_by_id.return_value = mock_user
    
    mock_receipt_repo = Mock()
    mock_receipt_repo.find_by_user_id.return_value = []
    mock_receipt_repo.find_split_transactions_by_user.return_value = []
    mock_receipt_repo.find_by_uploader.return_value = []
    mock_receipt_repo.find_pending_split_requests.return_value = []
    
    mock_coupon_repo = Mock()
    mock_coupon_repo.get_by_user.return_value = []
    
    mock_store_repo = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, coupon_repo=mock_coupon_repo, store_repo=mock_store_repo)
    client = app.test_client()
    response = client.get('/dashboard/user123')
    
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert "홍길동" in response_text
    assert "25000" in response_text


def test_should_display_recent_transactions():
    mock_user_repo = Mock()
    mock_user = Mock(name="홍길동", deposit=25000)
    mock_user_repo.get_by_id.return_value = mock_user
    
    mock_receipt_repo = Mock()
    mock_receipt = Mock(store_name="테스트 매장", total_amount=15000)
    mock_receipt_repo.find_by_user_id.return_value = [mock_receipt]
    mock_receipt_repo.find_split_transactions_by_user.return_value = []
    mock_receipt_repo.find_by_uploader.return_value = []
    mock_receipt_repo.find_pending_split_requests.return_value = []
    
    mock_coupon_repo = Mock()
    mock_coupon_repo.get_by_user.return_value = []
    
    mock_store_repo = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, coupon_repo=mock_coupon_repo, store_repo=mock_store_repo)
    client = app.test_client()
    response = client.get('/dashboard/user123')
    
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert "테스트 매장" in response_text
    assert "15000" in response_text


def test_should_display_coupon_progress():
    mock_user_repo = Mock()
    mock_user = Mock(name="홍길동", deposit=25000)
    mock_user_repo.get_by_id.return_value = mock_user
    
    mock_receipt_repo = Mock()
    mock_receipt_repo.find_by_user_id.return_value = []
    mock_receipt_repo.find_split_transactions_by_user.return_value = []
    mock_receipt_repo.find_by_uploader.return_value = []
    mock_receipt_repo.find_pending_split_requests.return_value = []
    
    mock_coupon_repo = Mock()
    mock_coupon = Mock(store_name="테스트 매장", count=3, goal=5)
    mock_coupon_repo.get_by_user.return_value = [mock_coupon]
    
    mock_store_repo = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, coupon_repo=mock_coupon_repo, store_repo=mock_store_repo)
    client = app.test_client()
    response = client.get('/dashboard/user123')
    
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert "테스트 매장" in response_text
    assert "3" in response_text
    assert "5" in response_text


def test_should_return_404_for_invalid_user():
    mock_user_repo = Mock()
    mock_user_repo.get_by_id.return_value = None  # User not found
    
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, coupon_repo=mock_coupon_repo, store_repo=mock_store_repo)
    client = app.test_client()
    response = client.get('/dashboard/nonexistent')
    
    assert response.status_code == 404


def test_should_show_split_payment_history():
    mock_user_repo = Mock()
    mock_user = Mock(name="홍길동", deposit=25000)
    mock_user_repo.get_by_id.return_value = mock_user
    
    mock_receipt_repo = Mock()
    mock_receipt_repo.find_by_user_id.return_value = []
    mock_receipt_repo.find_by_uploader.return_value = []
    mock_receipt_repo.find_pending_split_requests.return_value = []
    
    # Mock split payment history
    split_transaction1 = {
        'receipt_id': 'receipt123',
        'user_amount': 8000,
        'total_amount': 20000,
        'store_name': '스타벅스',
        'created_at': '2024-01-15'
    }
    split_transaction2 = {
        'receipt_id': 'receipt456', 
        'user_amount': 5500,
        'total_amount': 15000,
        'store_name': '맥도날드',
        'created_at': '2024-01-20'
    }
    mock_receipt_repo.find_split_transactions_by_user.return_value = [split_transaction1, split_transaction2]
    
    mock_coupon_repo = Mock()
    mock_coupon_repo.get_by_user.return_value = []
    
    mock_store_repo = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, coupon_repo=mock_coupon_repo, store_repo=mock_store_repo)
    client = app.test_client()
    response = client.get('/dashboard/user123')
    
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert "스타벅스" in response_text
    assert "8000" in response_text
    assert "맥도날드" in response_text
    assert "5500" in response_text
    mock_receipt_repo.find_split_transactions_by_user.assert_called_once_with("user123")


def test_should_display_receipts_uploaded_by_user():
    mock_user_repo = Mock()
    mock_user = Mock(name="홍길동", deposit=25000)
    mock_user_repo.get_by_id.return_value = mock_user
    
    mock_receipt_repo = Mock()
    mock_receipt_repo.find_by_user_id.return_value = []
    mock_receipt_repo.find_split_transactions_by_user.return_value = []
    mock_receipt_repo.find_pending_split_requests.return_value = []
    
    # Mock uploaded receipts
    uploaded_receipt1 = {
        'id': 'receipt789',
        'store_name': '올리브영',
        'total_amount': 12000,
        'created_at': '2024-01-10'
    }
    uploaded_receipt2 = {
        'id': 'receipt890',
        'store_name': 'GS25',
        'total_amount': 3500,
        'created_at': '2024-01-18'
    }
    mock_receipt_repo.find_by_uploader.return_value = [uploaded_receipt1, uploaded_receipt2]
    
    mock_coupon_repo = Mock()
    mock_coupon_repo.get_by_user.return_value = []
    
    mock_store_repo = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, coupon_repo=mock_coupon_repo, store_repo=mock_store_repo)
    client = app.test_client()
    response = client.get('/dashboard/user123')
    
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert "올리브영" in response_text
    assert "12000" in response_text
    assert "GS25" in response_text
    assert "3500" in response_text
    mock_receipt_repo.find_by_uploader.assert_called_once_with("user123")


def test_should_show_pending_split_requests():
    mock_user_repo = Mock()
    mock_user = Mock(name="홍길동", deposit=25000)
    mock_user_repo.get_by_id.return_value = mock_user
    
    mock_receipt_repo = Mock()
    mock_receipt_repo.find_by_user_id.return_value = []
    mock_receipt_repo.find_split_transactions_by_user.return_value = []
    mock_receipt_repo.find_by_uploader.return_value = []
    
    # Mock pending split requests - receipts where user is participant but no split recorded yet
    pending_request1 = {
        'id': 'receipt999',
        'store_name': '이마트',
        'total_amount': 45000,
        'uploader_name': '김철수',
        'created_at': '2024-01-25'
    }
    pending_request2 = {
        'id': 'receipt888',
        'store_name': '코스트코',
        'total_amount': 89000,
        'uploader_name': '박영희',
        'created_at': '2024-01-30'
    }
    mock_receipt_repo.find_pending_split_requests.return_value = [pending_request1, pending_request2]
    
    mock_coupon_repo = Mock()
    mock_coupon_repo.get_by_user.return_value = []
    
    mock_store_repo = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, coupon_repo=mock_coupon_repo, store_repo=mock_store_repo)
    client = app.test_client()
    response = client.get('/dashboard/user123')
    
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert "이마트" in response_text
    assert "45000" in response_text
    assert "김철수" in response_text
    assert "코스트코" in response_text
    assert "89000" in response_text
    assert "박영희" in response_text
    mock_receipt_repo.find_pending_split_requests.assert_called_once_with("user123")
