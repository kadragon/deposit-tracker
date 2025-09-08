import pytest
from unittest.mock import Mock
from src.web.app import create_app


def test_should_display_items_for_user_assignment():
    # Given: Mock dependencies
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    
    # Given: Test store
    mock_store = Mock(id='store1', name='카페 테스트')
    mock_store_repo.get_by_id.return_value = mock_store
    
    # Given: Test users
    user1 = Mock(id='user1', name='김철수')
    user2 = Mock(id='user2', name='이영희')
    mock_user_repo.list_all.return_value = [user1, user2]
    
    # Given: Test receipt items from session
    app = create_app(
        user_repo=mock_user_repo,
        receipt_repo=mock_receipt_repo,
        coupon_repo=mock_coupon_repo,
        ocr_service=mock_ocr_service,
        store_repo=mock_store_repo
    )
    
    client = app.test_client()
    
    # When: Visit item assignment page with store and items
    with client.session_transaction() as session:
        session['parsed_items'] = [
            {'name': '아메리카노', 'price': 4500, 'quantity': 1},
            {'name': '카페라떼', 'price': 5000, 'quantity': 2}
        ]
    
    response = client.get('/assign-items?store_id=store1')
    
    # Then: Page displays items and users for assignment
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert 'item-assignment' in text
    assert '카페 테스트' in text
    assert '아메리카노' in text
    assert '4500' in text
    assert '카페라떼' in text
    assert '5000' in text
    assert '김철수' in text
    assert '이영희' in text


def test_should_display_all_users_for_item_assignment():
    # Given: Mock dependencies with multiple users
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    
    # Given: Test store
    mock_store = Mock(id='store1', name='스타벅스')
    mock_store_repo.get_by_id.return_value = mock_store
    
    # Given: Multiple test users
    user1 = Mock(id='user1', name='김철수')
    user2 = Mock(id='user2', name='이영희')
    user3 = Mock(id='user3', name='박민수')
    user4 = Mock(id='user4', name='최지은')
    mock_user_repo.list_all.return_value = [user1, user2, user3, user4]
    
    app = create_app(
        user_repo=mock_user_repo,
        receipt_repo=mock_receipt_repo,
        coupon_repo=mock_coupon_repo,
        ocr_service=mock_ocr_service,
        store_repo=mock_store_repo
    )
    
    client = app.test_client()
    
    # When: Visit item assignment page
    with client.session_transaction() as session:
        session['parsed_items'] = [
            {'name': '아메리카노', 'price': 4500, 'quantity': 1}
        ]
    
    response = client.get('/assign-items?store_id=store1')
    
    # Then: All users should be displayed for assignment
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert 'user-list' in text
    assert '김철수' in text
    assert '이영희' in text
    assert '박민수' in text
    assert '최지은' in text


def test_should_allow_assigning_items_to_users():
    # Given: Mock dependencies
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    
    # Given: Test store
    mock_store = Mock(id='store1', name='카페베네')
    mock_store_repo.get_by_id.return_value = mock_store
    
    # Given: Test users
    user1 = Mock(id='user1', name='김철수')
    user2 = Mock(id='user2', name='이영희')
    mock_user_repo.list_all.return_value = [user1, user2]
    
    app = create_app(
        user_repo=mock_user_repo,
        receipt_repo=mock_receipt_repo,
        coupon_repo=mock_coupon_repo,
        ocr_service=mock_ocr_service,
        store_repo=mock_store_repo
    )
    
    client = app.test_client()
    
    # When: Submit item assignments
    assignment_data = {
        'store_id': 'store1',
        'item_assignments': [
            {'item_index': '0', 'user_id': 'user1'},  # 아메리카노 -> 김철수
            {'item_index': '1', 'user_id': 'user2'}   # 카페라떼 -> 이영희
        ]
    }
    
    with client.session_transaction() as session:
        session['parsed_items'] = [
            {'name': '아메리카노', 'price': 4500, 'quantity': 1},
            {'name': '카페라떼', 'price': 5000, 'quantity': 1}
        ]
    
    response = client.post('/assign-items', json=assignment_data)
    
    # Then: Assignment should be processed successfully
    assert response.status_code == 200
    data = response.get_json()
    assert 'assignment-success' in str(data)
    assert 'user1' in str(data)
    assert 'user2' in str(data)


def test_should_support_item_sharing_selection():
    # Given: Mock dependencies
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    
    # Given: Test store
    mock_store = Mock(id='store1', name='맥도날드')
    mock_store_repo.get_by_id.return_value = mock_store
    
    # Given: Test users
    user1 = Mock(id='user1', name='김철수')
    user2 = Mock(id='user2', name='이영희')
    user3 = Mock(id='user3', name='박민수')
    mock_user_repo.list_all.return_value = [user1, user2, user3]
    
    app = create_app(
        user_repo=mock_user_repo,
        receipt_repo=mock_receipt_repo,
        coupon_repo=mock_coupon_repo,
        ocr_service=mock_ocr_service,
        store_repo=mock_store_repo
    )
    
    client = app.test_client()
    
    # When: Submit item assignments with sharing
    sharing_data = {
        'store_id': 'store1',
        'item_assignments': [
            {
                'item_index': '0', 
                'sharing_type': 'shared',
                'shared_users': ['user1', 'user2', 'user3'],  # 빅맥 세트를 3명이 공유
                'sharing_ratio': [0.4, 0.4, 0.2]  # 김철수 40%, 이영희 40%, 박민수 20%
            },
            {
                'item_index': '1',
                'sharing_type': 'individual', 
                'user_id': 'user2'  # 콜라는 이영희 개인
            }
        ]
    }
    
    with client.session_transaction() as session:
        session['parsed_items'] = [
            {'name': '빅맥세트', 'price': 8500, 'quantity': 1},
            {'name': '콜라', 'price': 2000, 'quantity': 1}
        ]
    
    response = client.post('/assign-items', json=sharing_data)
    
    # Then: Sharing assignment should be processed
    assert response.status_code == 200
    data = response.get_json()
    assert 'assignment-success' in str(data)
    
    # And: Should contain sharing information
    assignments = data.get('assignments', [])
    shared_assignment = assignments[0]
    assert shared_assignment['sharing_type'] == 'shared'
    assert len(shared_assignment['shared_users']) == 3
    assert shared_assignment['sharing_ratio'] == [0.4, 0.4, 0.2]
    
    individual_assignment = assignments[1]
    assert individual_assignment['sharing_type'] == 'individual'
    assert individual_assignment['user_id'] == 'user2'


def test_should_show_real_time_amount_calculation():
    # Given: Mock dependencies
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    
    # Given: Test store and users
    mock_store = Mock(id='store1', name='피자헛')
    mock_store_repo.get_by_id.return_value = mock_store
    
    user1 = Mock(id='user1', name='김철수')
    user2 = Mock(id='user2', name='이영희')
    mock_user_repo.list_all.return_value = [user1, user2]
    
    app = create_app(
        user_repo=mock_user_repo,
        receipt_repo=mock_receipt_repo,
        coupon_repo=mock_coupon_repo,
        ocr_service=mock_ocr_service,
        store_repo=mock_store_repo
    )
    
    client = app.test_client()
    
    # When: Request calculation with assignments
    calculation_data = {
        'store_id': 'store1',
        'item_assignments': [
            {'item_index': '0', 'user_id': 'user1'},  # 피자 -> 김철수 (15000원)
            {'item_index': '1', 'user_id': 'user2'}   # 콜라 -> 이영희 (2000원)
        ]
    }
    
    with client.session_transaction() as session:
        session['parsed_items'] = [
            {'name': '피자', 'price': 15000, 'quantity': 1},
            {'name': '콜라', 'price': 2000, 'quantity': 1}
        ]
    
    response = client.post('/calculate-amounts', json=calculation_data)
    
    # Then: Should return calculated amounts per user
    assert response.status_code == 200
    data = response.get_json()
    assert 'calculation-result' in str(data)
    
    user_amounts = data.get('user_amounts', {})
    assert user_amounts['user1'] == 15000  # 김철수: 피자 15000원
    assert user_amounts['user2'] == 2000   # 이영희: 콜라 2000원
    assert data.get('total_amount') == 17000


def test_should_validate_all_items_assigned_before_submit():
    # Given: Mock dependencies
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_ocr_service = Mock()
    mock_store_repo = Mock()
    
    # Given: Test setup
    mock_store = Mock(id='store1', name='버거킹')
    mock_store_repo.get_by_id.return_value = mock_store
    
    user1 = Mock(id='user1', name='김철수')
    mock_user_repo.list_all.return_value = [user1]
    
    app = create_app(
        user_repo=mock_user_repo,
        receipt_repo=mock_receipt_repo,
        coupon_repo=mock_coupon_repo,
        ocr_service=mock_ocr_service,
        store_repo=mock_store_repo
    )
    
    client = app.test_client()
    
    # When: Submit with incomplete assignments (missing item 1)
    incomplete_data = {
        'store_id': 'store1',
        'item_assignments': [
            {'item_index': '0', 'user_id': 'user1'}  # 와퍼만 배정, 감자튀김 미배정
        ]
    }
    
    with client.session_transaction() as session:
        session['parsed_items'] = [
            {'name': '와퍼', 'price': 8000, 'quantity': 1},
            {'name': '감자튀김', 'price': 3000, 'quantity': 1}  # 이 아이템이 배정되지 않음
        ]
    
    response = client.post('/validate-assignments', json=incomplete_data)
    
    # Then: Should return validation error
    assert response.status_code == 400
    data = response.get_json()
    assert 'validation-error' in str(data)
    assert 'unassigned-items' in str(data)
    assert len(data.get('unassigned_items', [])) == 1
    assert data['unassigned_items'][0]['name'] == '감자튀김'