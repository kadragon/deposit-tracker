import pytest
from flask import Flask
from src.web.app import create_app
from unittest.mock import Mock, patch


def test_should_display_user_selection_page():
    mock_user_repo = Mock()
    mock_user_repo.list_all.return_value = []
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    client = app.test_client()
    response = client.get('/')
    
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '사용자를 선택해주세요' in html


def test_should_list_all_available_users():
    mock_user_repo = Mock()
    mock_user_repo.list_all.return_value = [
        Mock(name="홍길동", id="user1"),
        Mock(name="김철수", id="user2")
    ]
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    client = app.test_client()
    response = client.get('/')
    
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert "홍길동" in response_text
    assert "김철수" in response_text


def test_should_redirect_to_dashboard_when_user_selected():
    mock_user_repo = Mock()
    mock_user_repo.list_all.return_value = []
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    client = app.test_client()
    response = client.post('/', data={'user_id': 'user123'})
    
    assert response.status_code == 302
    assert '/dashboard/user123' in response.location
