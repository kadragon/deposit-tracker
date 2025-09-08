import pytest
from unittest.mock import Mock
from decimal import Decimal
from src.web.app import create_app


def test_should_display_per_user_payment_summary():
    # Given: Mock dependencies
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    
    # Given: Test store and users with deposits
    mock_store = Mock(id='store1', name='스타벅스')
    mock_store_repo.get_by_id.return_value = mock_store
    
    user1 = Mock(id='user1', name='김철수', deposit=Decimal('50000'))
    user2 = Mock(id='user2', name='이영희', deposit=Decimal('30000'))
    mock_user_repo.get_by_id.side_effect = lambda uid: user1 if uid == 'user1' else user2
    
    app = create_app(
        user_repo=mock_user_repo,
        receipt_repo=mock_receipt_repo,
        coupon_repo=mock_coupon_repo,
        ocr_service=mock_ocr_service,
        store_repo=mock_store_repo
    )
    
    client = app.test_client()
    
    # When: Request payment summary
    with client.session_transaction() as session:
        session['split_assignments'] = {
            'user1': 15000,  # 김철수: 15000원
            'user2': 8500    # 이영희: 8500원
        }
        session['assignment_store_id'] = 'store1'
    
    response = client.get('/payment-summary')
    
    # Then: Should display per-user payment summary
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert 'payment-summary' in text
    assert '김철수' in text
    assert '15000' in text
    assert '이영희' in text
    assert '8500' in text
    assert 'deposit-balance' in text


def test_should_show_insufficient_balance_warnings():
    # Given: Mock dependencies
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    
    # Given: User with insufficient deposit
    mock_store = Mock(id='store1', name='맥도날드')
    mock_store_repo.get_by_id.return_value = mock_store
    
    user1 = Mock(id='user1', name='김철수', deposit=Decimal('50000'))
    user2 = Mock(id='user2', name='이영희', deposit=Decimal('5000'))  # 부족한 잔액
    mock_user_repo.get_by_id.side_effect = lambda uid: user1 if uid == 'user1' else user2
    
    app = create_app(
        user_repo=mock_user_repo,
        receipt_repo=mock_receipt_repo,
        coupon_repo=mock_coupon_repo,
        ocr_service=mock_ocr_service,
        store_repo=mock_store_repo
    )
    
    client = app.test_client()
    
    # When: Request payment summary with insufficient balance
    with client.session_transaction() as session:
        session['split_assignments'] = {
            'user1': 15000,  # 김철수: 충분한 잔액
            'user2': 8500    # 이영희: 부족한 잔액 (5000 < 8500)
        }
        session['assignment_store_id'] = 'store1'
    
    response = client.get('/payment-summary')
    
    # Then: Should show insufficient balance warning
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert 'insufficient-balance-warning' in text
    assert '이영희' in text
    assert 'user2' in text


def test_should_allow_payment_method_selection_per_user():
    # Given: Mock dependencies
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    
    mock_store = Mock(id='store1', name='버거킹')
    mock_store_repo.get_by_id.return_value = mock_store
    
    user1 = Mock(id='user1', name='김철수', deposit=Decimal('50000'))
    user2 = Mock(id='user2', name='이영희', deposit=Decimal('10000'))
    mock_user_repo.get_by_id.side_effect = lambda uid: user1 if uid == 'user1' else user2
    
    app = create_app(
        user_repo=mock_user_repo,
        receipt_repo=mock_receipt_repo,
        coupon_repo=mock_coupon_repo,
        ocr_service=mock_ocr_service,
        store_repo=mock_store_repo
    )
    
    client = app.test_client()
    
    # When: Submit payment method selections
    payment_data = {
        'store_id': 'store1',
        'user_payments': [
            {'user_id': 'user1', 'amount': 12000, 'method': 'deposit'},
            {'user_id': 'user2', 'amount': 7000, 'method': 'cash'}  # 현금 결제 선택
        ]
    }
    
    response = client.post('/select-payment-methods', json=payment_data)
    
    # Then: Should accept payment method selections
    assert response.status_code == 200
    data = response.get_json()
    assert 'payment-methods-selected' in str(data)
    
    user_payments = data.get('user_payments', [])
    assert len(user_payments) == 2
    assert user_payments[0]['method'] == 'deposit'
    assert user_payments[1]['method'] == 'cash'


def test_should_process_multi_user_payment():
    # Given: Mock dependencies
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    mock_coupon_service = Mock()
    
    # Given: Users with sufficient deposits
    mock_store = Mock(id='store1', name='KFC')
    mock_store_repo.get_by_id.return_value = mock_store
    
    user1 = Mock(id='user1', name='김철수', deposit=Decimal('50000'))
    user2 = Mock(id='user2', name='이영희', deposit=Decimal('30000'))
    mock_user_repo.get_by_id.side_effect = lambda uid: user1 if uid == 'user1' else user2
    
    app = create_app(
        user_repo=mock_user_repo,
        receipt_repo=mock_receipt_repo,
        coupon_repo=mock_coupon_repo,
        ocr_service=mock_ocr_service,
        store_repo=mock_store_repo,
        coupon_service=mock_coupon_service
    )
    
    client = app.test_client()
    
    # When: Process multi-user payment
    payment_data = {
        'store_id': 'store1',
        'user_payments': [
            {'user_id': 'user1', 'amount': 15000, 'method': 'deposit'},
            {'user_id': 'user2', 'amount': 8500, 'method': 'deposit'}
        ]
    }
    
    response = client.post('/process-split-payment', json=payment_data)
    
    # Then: Should process payments successfully
    assert response.status_code == 200
    data = response.get_json()
    assert 'multi-user-payment-success' in str(data)
    
    # And: Should deduct from user deposits
    user1.subtract_deposit.assert_called_once_with(Decimal('15000'))
    user2.subtract_deposit.assert_called_once_with(Decimal('8500'))
    
    # And: Should save updated users
    assert mock_user_repo.save.call_count == 2
    
    # And: Should award coupons to deposit payers only
    mock_coupon_service.award_coupon_for_purchase.assert_any_call('user1', 'store1')
    mock_coupon_service.award_coupon_for_purchase.assert_any_call('user2', 'store1')