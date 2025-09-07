import pytest
from flask import Flask
from src.web.app import create_app
from unittest.mock import Mock


def test_should_update_user_deposit_after_transaction():
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    mock_coupon_service = Mock()

    # Mock user with deposit
    mock_user = Mock(id='user1', name='User 1', deposit=10000)
    mock_user_repo.get_by_id.return_value = mock_user

    app = create_app(
        user_repo=mock_user_repo,
        receipt_repo=mock_receipt_repo,
        coupon_repo=mock_coupon_repo,
        ocr_service=mock_ocr_service,
        store_repo=mock_store_repo,
        coupon_service=mock_coupon_service,
    )
    client = app.test_client()

    # Process transaction with deposit
    response = client.post('/process-receipt', data={
        'user_id': 'user1',
        'store_id': 'store123',
        'total': '5000',
        'use_deposit': 'yes'
    })

    assert response.status_code == 302  # Redirects on success
    # Verify user's subtract_deposit was called
    mock_user.subtract_deposit.assert_called_once()
    # Accept Decimal or str; don't over-constrain type here
    mock_user_repo.save.assert_called_once_with(mock_user)


def test_should_award_coupon_after_transaction():
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    mock_coupon_service = Mock()

    # Mock user
    mock_user = Mock(id='user1', name='User 1')
    mock_user_repo.get_by_id.return_value = mock_user

    app = create_app(
        user_repo=mock_user_repo,
        receipt_repo=mock_receipt_repo,
        coupon_repo=mock_coupon_repo,
        ocr_service=mock_ocr_service,
        store_repo=mock_store_repo,
        coupon_service=mock_coupon_service,
    )
    client = app.test_client()

    # Process transaction
    response = client.post('/process-receipt', data={
        'user_id': 'user1',
        'store_id': 'store123',
        'total': '5000',
        'use_deposit': 'no'
    })

    assert response.status_code == 302  # Redirect
    # Verify coupon service was called with canonical method
    mock_coupon_service.award_coupon_for_purchase.assert_called_once_with('user1', 'store123')


def test_should_redirect_to_success_page():
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    mock_coupon_service = Mock()

    app = create_app(
        user_repo=mock_user_repo,
        receipt_repo=mock_receipt_repo,
        coupon_repo=mock_coupon_repo,
        ocr_service=mock_ocr_service,
        store_repo=mock_store_repo,
        coupon_service=mock_coupon_service,
    )
    client = app.test_client()

    # Process transaction
    response = client.post('/process-receipt', data={
        'user_id': 'user1',
        'store_id': 'store123',
        'total': '5000',
        'use_deposit': 'no'
    })

    assert response.status_code == 302  # Redirect status
    assert 'success' in response.location


def test_should_return_400_when_insufficient_deposit():
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    mock_coupon_service = Mock()

    # User has insufficient deposit
    mock_user = Mock(id='user1', name='User 1', deposit=3000)
    mock_user_repo.get_by_id.return_value = mock_user

    app = create_app(
        user_repo=mock_user_repo,
        receipt_repo=mock_receipt_repo,
        coupon_repo=mock_coupon_repo,
        ocr_service=mock_ocr_service,
        store_repo=mock_store_repo,
        coupon_service=mock_coupon_service,
    )
    client = app.test_client()

    response = client.post('/process-receipt', data={
        'user_id': 'user1',
        'store_id': 'store123',
        'total': '5000',
        'use_deposit': 'yes'
    })

    assert response.status_code == 400
    assert 'Insufficient deposit' in response.get_data(as_text=True)
