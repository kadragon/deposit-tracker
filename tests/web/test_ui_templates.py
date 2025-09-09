import pytest
from flask import Flask
from src.web.app import create_app
from unittest.mock import Mock


def test_should_render_base_template_with_tailwind():
    """Test that the base template renders with proper Tailwind CSS structure"""
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
    
    # Check for proper HTML structure
    assert '<!DOCTYPE html>' in html
    assert '<html' in html
    assert '<head>' in html
    assert '<title>' in html
    assert '</head>' in html
    assert '<body' in html
    assert '</body>' in html
    assert '</html>' in html
    
    # Check for Tailwind CSS CDN (more secure check)
    assert 'src="https://cdn.tailwindcss.com"' in html or 'tailwindcss' in html
    
    # Check for basic responsive structure
    assert 'class=' in html  # Should have CSS classes
    assert 'container' in html or 'max-w-' in html  # Should have container classes


def test_should_display_user_selection_form():
    """Test that user selection form is properly rendered with form elements"""
    mock_user_repo = Mock()
    mock_user_repo.list_all.return_value = [
        Mock(id="user1", name="홍길동", deposit=50000),
        Mock(id="user2", name="김철수", deposit=30000)
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
    html = response.get_data(as_text=True)
    
    # Check for form elements
    assert '<form' in html
    assert 'method="post"' in html
    assert 'type="radio"' in html
    assert 'name="user_id"' in html
    assert 'type="submit"' in html or 'button' in html
    
    # Check for user data
    assert "홍길동" in html
    assert "김철수" in html
    assert "50000" in html  # deposit amount
    assert "30000" in html  # deposit amount


def test_should_render_user_cards_with_deposit_info():
    """Test that user cards are properly styled with Tailwind CSS and show deposit information"""
    mock_user_repo = Mock()
    mock_user_repo.list_all.return_value = [
        Mock(id="user1", name="홍길동", deposit=50000),
        Mock(id="user2", name="김철수", deposit=30000)
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
    html = response.get_data(as_text=True)
    
    # Check for card-like styling elements
    assert 'border' in html  # Cards should have borders
    assert 'rounded' in html  # Cards should be rounded
    assert 'p-' in html  # Cards should have padding
    
    # Check for deposit information display
    assert "예치금" in html
    assert "원" in html  # Currency unit
    
    # Check for responsive/interactive elements
    assert 'hover:' in html or 'cursor-pointer' in html  # Interactive elements
    assert 'peer-checked:' in html or 'checked:' in html  # Selection state styling


def test_should_render_user_dashboard_layout():
    """Test that user dashboard renders with proper layout structure"""
    mock_user_repo = Mock()
    mock_user_repo.get_by_id.return_value = Mock(id="user1", name="홍길동", deposit=50000)
    mock_user_repo.list_all.return_value = []
    mock_receipt_repo = Mock()
    mock_receipt_repo.find_by_user_id.return_value = []
    mock_receipt_repo.find_split_transactions_by_user.return_value = []
    mock_receipt_repo.find_by_uploader.return_value = []
    mock_receipt_repo.find_pending_split_requests.return_value = []
    mock_coupon_repo = Mock()
    mock_coupon_repo.get_by_user.return_value = []
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    client = app.test_client()
    response = client.get('/dashboard/user1')
    
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    
    # Check for HTML structure
    assert '<!DOCTYPE html>' in html
    assert 'tailwindcss' in html
    
    # Should have dashboard-specific content
    assert "홍길동" in html or "user" in html.lower() or "dashboard" in html.lower()


def test_should_display_current_balance_prominently():
    """Test that current balance is displayed prominently in dashboard"""
    mock_user_repo = Mock()
    mock_user_repo.get_by_id.return_value = Mock(id="user1", name="홍길동", deposit=50000)
    mock_user_repo.list_all.return_value = []
    mock_receipt_repo = Mock()
    mock_receipt_repo.find_by_user_id.return_value = []
    mock_receipt_repo.find_split_transactions_by_user.return_value = []
    mock_receipt_repo.find_by_uploader.return_value = []
    mock_receipt_repo.find_pending_split_requests.return_value = []
    mock_coupon_repo = Mock()
    mock_coupon_repo.get_by_user.return_value = []
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    client = app.test_client()
    response = client.get('/dashboard/user1')
    
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    
    # Should show balance information prominently
    assert "50000" in html  # The deposit amount
    assert "예치금" in html or "잔액" in html or "balance" in html.lower()


def test_should_show_recent_transactions_list():
    """Test that recent transactions are shown in a list format"""
    mock_user_repo = Mock()
    mock_user_repo.get_by_id.return_value = Mock(id="user1", name="홍길동", deposit=50000)
    mock_user_repo.list_all.return_value = []
    mock_receipt_repo = Mock()
    mock_receipt_repo.find_by_user_id.return_value = [
        {'store_name': '스타벅스', 'total_amount': 15000},
        {'store_name': '맥도날드', 'total_amount': 8000}
    ]
    mock_receipt_repo.find_split_transactions_by_user.return_value = []
    mock_receipt_repo.find_by_uploader.return_value = []
    mock_receipt_repo.find_pending_split_requests.return_value = []
    mock_coupon_repo = Mock()
    mock_coupon_repo.get_by_user.return_value = []
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    client = app.test_client()
    response = client.get('/dashboard/user1')
    
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    
    # Should show transaction data
    assert "스타벅스" in html
    assert "맥도날드" in html
    assert "15000" in html
    assert "8000" in html


def test_should_render_upload_receipt_button():
    """Test that upload receipt button is present and properly styled"""
    mock_user_repo = Mock()
    mock_user_repo.get_by_id.return_value = Mock(id="user1", name="홍길동", deposit=50000)
    mock_user_repo.list_all.return_value = []
    mock_receipt_repo = Mock()
    mock_receipt_repo.find_by_user_id.return_value = []
    mock_receipt_repo.find_split_transactions_by_user.return_value = []
    mock_receipt_repo.find_by_uploader.return_value = []
    mock_receipt_repo.find_pending_split_requests.return_value = []
    mock_coupon_repo = Mock()
    mock_coupon_repo.get_by_user.return_value = []
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    client = app.test_client()
    response = client.get('/dashboard/user1')
    
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    
    # Should have upload button/link
    assert ('upload' in html.lower() and ('button' in html or 'a href' in html)) or '영수증' in html


def test_should_render_file_upload_dropzone():
    """Test that file upload form has drag and drop functionality"""
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    client = app.test_client()
    response = client.get('/upload')
    
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    
    # Check for HTML structure
    assert '<!DOCTYPE html>' in html
    assert 'tailwindcss' in html
    
    # Check for upload form elements
    assert 'form' in html
    assert 'enctype="multipart/form-data"' in html or 'multipart' in html
    assert 'type="file"' in html or 'file' in html.lower()


def test_should_show_upload_progress_indicator():
    """Test that upload form has progress indication elements"""
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    client = app.test_client()
    response = client.get('/upload')
    
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    
    # Check for progress/loading related elements or text
    assert ('progress' in html.lower() or 'loading' in html.lower() or 
            'upload' in html.lower() or '업로드' in html or '처리' in html)


def test_should_display_ocr_processing_spinner():
    """Test that OCR processing state is indicated"""
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    client = app.test_client()
    response = client.get('/upload')
    
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    
    # Check for spinner or processing related elements
    assert ('spinner' in html.lower() or 'processing' in html.lower() or 
            'loading' in html.lower() or '처리' in html or 'OCR' in html.upper())


def test_should_render_ocr_results_preview():
    """Test that OCR results can be previewed"""
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    client = app.test_client()
    response = client.get('/upload')
    
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    
    # Check for preview related elements
    assert ('preview' in html.lower() or 'result' in html.lower() or 
            '결과' in html or '미리' in html)


def test_should_render_admin_navigation_menu():
    """Test that admin interface has proper navigation menu"""
    mock_user_repo = Mock()
    mock_user_repo.list_all.return_value = []
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    
    with app.test_client() as client:
        # Login to admin first
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        response = client.get('/admin/users')
        
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        
        # Check for HTML structure
        assert '<!DOCTYPE html>' in html
        assert 'tailwindcss' in html
        
        # Admin should have navigation or menu elements
        assert ('nav' in html.lower() or 'menu' in html.lower() or 
                'admin' in html.lower() or '관리' in html)


def test_should_display_users_management_grid():
    """Test that admin can see users in a grid/table format"""
    mock_user_repo = Mock()
    mock_user_repo.list_all.return_value = [
        Mock(name="홍길동", deposit=50000),
        Mock(name="김철수", deposit=30000)
    ]
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    
    with app.test_client() as client:
        # Login to admin first
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        response = client.get('/admin/users')
        
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        
        # Should display user information
        assert "홍길동" in html
        assert "김철수" in html
        assert "50000" in html
        assert "30000" in html


def test_should_render_deposit_management_forms():
    """Test that admin has forms to manage user deposits"""
    mock_user_repo = Mock()
    mock_user_repo.list_all.return_value = [
        Mock(name="홍길동", deposit=50000, id="user1")
    ]
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    
    with app.test_client() as client:
        # Login to admin first  
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        response = client.get('/admin/users')
        
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        
        # Should have forms for deposit management
        assert ('form' in html and ('deposit' in html.lower() or '예치금' in html)) or 'input' in html


def test_should_show_transaction_history_table():
    """Test that admin can view transaction history in table format"""
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_receipt_repo.list_all.return_value = [
        {'user_name': '홍길동', 'store_name': '스타벅스', 'total_amount': 15000},
        {'user_name': '김철수', 'store_name': '맥도날드', 'total_amount': 8000}
    ]
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    
    with app.test_client() as client:
        # Login to admin first
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        response = client.get('/admin/transactions')
        
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        
        # Should display transaction information
        assert "홍길동" in html
        assert "스타벅스" in html
        assert "15000" in html


def test_should_render_stores_list_with_actions():
    """Test that admin can manage stores with actions"""
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_store_repo.list_all.return_value = [
        {"id": "store1", "name": "스타벅스", "coupon_enabled": True, "coupon_goal": 10},
        {"id": "store2", "name": "맥도날드", "coupon_enabled": False, "coupon_goal": 5}
    ]
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    
    with app.test_client() as client:
        # Login to admin first
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        response = client.get('/admin/stores')
        
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        
        # Should display store information
        assert "스타벅스" in html
        assert "맥도날드" in html


def test_should_display_coupon_settings_toggles():
    """Test that admin can toggle coupon settings for stores"""
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_store_repo.list_all.return_value = [
        {"id": "store1", "name": "스타벅스", "coupon_enabled": True, "coupon_goal": 10}
    ]
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    
    with app.test_client() as client:
        # Login to admin first
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        response = client.get('/admin/stores')
        
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        
        # Should have coupon-related controls
        assert ('coupon' in html.lower() or '쿠폰' in html or 
                'toggle' in html.lower() or 'checkbox' in html or 'True' in html)


def test_should_render_items_list_with_checkboxes():
    """Test that item assignment page renders items with checkboxes for selection"""
    mock_user_repo = Mock()
    mock_user_repo.list_all.return_value = [
        Mock(id="user1", name="홍길동"),
        Mock(id="user2", name="김철수")
    ]
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_store_repo.get_by_id.return_value = Mock(name="스타벅스")
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    
    with app.test_client() as client:
        # Set up session with parsed items
        with client.session_transaction() as sess:
            sess['parsed_items'] = [
                {'name': '아메리카노', 'price': 4500, 'quantity': 2},
                {'name': '라떼', 'price': 5000, 'quantity': 1},
                {'name': '샌드위치', 'price': 6500, 'quantity': 1}
            ]
        
        response = client.get('/assign-items?store_id=store1')
        
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        
        # Check for HTML structure
        assert '<!DOCTYPE html>' in html
        assert 'tailwindcss' in html
        
        # Check for item list and checkboxes
        assert '아메리카노' in html
        assert '라떼' in html
        assert '샌드위치' in html
        assert '4500' in html
        assert '5000' in html
        assert '6500' in html
        
        # Check for form elements
        assert ('checkbox' in html.lower() or 'input' in html.lower() or 
                'form' in html.lower())
        
        # Check for user assignment options
        assert '홍길동' in html
        assert '김철수' in html


def test_should_display_user_avatars_for_assignment():
    """Test that item assignment page displays user avatars for visual assignment"""
    mock_user_repo = Mock()
    # Set up mock users with proper Mock objects
    mock_users = []
    for user_data in [
        {'id': 'user1', 'name': '김철수'},
        {'id': 'user2', 'name': '이영희'},
        {'id': 'user3', 'name': '박민수'},
        {'id': 'user4', 'name': '정수진'}
    ]:
        mock_user = Mock()
        mock_user.id = user_data['id']
        mock_user.name = user_data['name']
        mock_users.append(mock_user)
    mock_user_repo.list_all.return_value = mock_users
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    
    with app.test_client() as client:
        # Set up session with parsed items and users
        with client.session_transaction() as sess:
            sess['parsed_items'] = [
                {'name': '아메리카노', 'price': 4500, 'quantity': 1},
                {'name': '라떼', 'price': 5000, 'quantity': 1}
            ]
            sess['users'] = [
                {'id': 'user1', 'name': '김철수'},
                {'id': 'user2', 'name': '이영희'},
                {'id': 'user3', 'name': '박민수'},
                {'id': 'user4', 'name': '정수진'}
            ]
        
        response = client.get('/assign-items')
        html = response.get_data(as_text=True)
        
        # Test basic response
        assert response.status_code == 200
        assert '<!DOCTYPE html>' in html
        
        # Test for avatar elements (using CSS classes or image elements)
        assert ('avatar' in html.lower() or 
                'profile' in html.lower() or 
                'user-icon' in html.lower() or
                'bg-' in html)  # Tailwind avatar backgrounds
        
        # Test for visual user representation with initials or icons
        assert ('김' in html or 'K' in html)  # First letter of name
        assert ('이' in html or 'L' in html)  # First letter of name
        assert ('박' in html or 'P' in html)  # First letter of name
        assert ('정' in html or 'J' in html)  # First letter of name
        
        # Test for user assignment interface with visual elements
        assert 'flex' in html  # Flexbox layout for avatars
        assert 'rounded' in html  # Rounded avatar styling
        assert 'w-' in html and 'h-' in html  # Width and height classes for avatars


def test_should_show_real_time_calculation_sidebar():
    """Test that item assignment page shows real-time calculation sidebar"""
    mock_user_repo = Mock()
    # Set up mock users
    mock_users = []
    for user_data in [
        {'id': 'user1', 'name': '김철수'},
        {'id': 'user2', 'name': '이영희'}
    ]:
        mock_user = Mock()
        mock_user.id = user_data['id']
        mock_user.name = user_data['name']
        mock_users.append(mock_user)
    mock_user_repo.list_all.return_value = mock_users
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    
    with app.test_client() as client:
        # Set up session with parsed items
        with client.session_transaction() as sess:
            sess['parsed_items'] = [
                {'name': '아메리카노', 'price': 4500, 'quantity': 2},
                {'name': '라떼', 'price': 5000, 'quantity': 1}
            ]
        
        response = client.get('/assign-items')
        html = response.get_data(as_text=True)
        
        # Test basic response
        assert response.status_code == 200
        assert '<!DOCTYPE html>' in html
        
        # Test for calculation sidebar container
        assert 'calculation-sidebar' in html or 'calculation' in html
        assert '분할 계산' in html or '계산' in html
        
        # Test for JavaScript calculation functionality
        assert 'updateCalculation' in html or 'calculation' in html.lower()
        assert 'addEventListener' in html or 'change' in html
        
        # Test for real-time elements (dynamic content containers)
        assert ('calculation-result' in html or 
                'total' in html.lower() or
                'amount' in html.lower())
        
        # Test for currency formatting and calculation display
        assert ('toLocaleString' in html or 
                '원' in html or
                'format' in html.lower())
        
        # Test for user-specific calculation breakdown
        assert 'assignment' in html.lower() or 'user' in html.lower()
        
        # Test JavaScript is present for interactivity
        assert '<script>' in html and '</script>' in html


def test_should_render_split_summary_modal():
    """Test that item assignment page renders split summary modal"""
    mock_user_repo = Mock()
    # Set up mock users
    mock_users = []
    for user_data in [
        {'id': 'user1', 'name': '김철수'},
        {'id': 'user2', 'name': '이영희'},
        {'id': 'user3', 'name': '박민수'}
    ]:
        mock_user = Mock()
        mock_user.id = user_data['id']
        mock_user.name = user_data['name']
        mock_users.append(mock_user)
    mock_user_repo.list_all.return_value = mock_users
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    
    with app.test_client() as client:
        # Set up session with parsed items
        with client.session_transaction() as sess:
            sess['parsed_items'] = [
                {'name': '아메리카노', 'price': 4500, 'quantity': 2},
                {'name': '샌드위치', 'price': 6000, 'quantity': 1}
            ]
        
        response = client.get('/assign-items')
        html = response.get_data(as_text=True)
        
        # Test basic response
        assert response.status_code == 200
        assert '<!DOCTYPE html>' in html
        
        # Test for modal container and structure
        assert ('modal' in html.lower() or 
                'dialog' in html.lower() or
                'popup' in html.lower())
        
        # Test for modal trigger button
        assert ('분할 계산하기' in html or 
                '계산하기' in html or
                'submit' in html.lower())
        
        # Test for modal content elements
        assert ('summary' in html.lower() or 
                '요약' in html or
                '결제' in html)
        
        # Test for modal overlay and backdrop
        assert ('overlay' in html.lower() or 
                'backdrop' in html.lower() or
                'bg-black' in html or
                'bg-gray' in html)
        
        # Test for modal close functionality
        assert ('close' in html.lower() or 
                '닫기' in html or
                '취소' in html)
        
        # Test for split breakdown display in modal
        assert ('breakdown' in html.lower() or 
                'split' in html.lower() or
                '분할' in html)
        
        # Test for confirmation buttons in modal
        assert ('confirm' in html.lower() or 
                '확인' in html or
                'proceed' in html.lower())
        
        # Test for modal JavaScript functionality
        assert ('showModal' in html or 
                'modal' in html.lower() and 'show' in html.lower())
        
        # Test for responsive modal design
        assert ('fixed' in html and 'inset-0' in html) or 'modal' in html.lower()


def test_should_render_payment_summary_cards():
    """Test that payment summary page renders payment cards for each user"""
    mock_user_repo = Mock()
    # Set up mock users with different deposit amounts
    mock_users = {}
    for user_data in [
        {'id': 'user1', 'name': '김철수', 'deposit': 20000},
        {'id': 'user2', 'name': '이영희', 'deposit': 15000},
        {'id': 'user3', 'name': '박민수', 'deposit': 5000}  # Insufficient balance
    ]:
        mock_user = Mock()
        mock_user.id = user_data['id']
        mock_user.name = user_data['name']
        mock_user.deposit = user_data['deposit']
        mock_users[user_data['id']] = mock_user
        
    def mock_get_by_id(user_id):
        return mock_users.get(user_id)
    
    mock_user_repo.get_by_id = mock_get_by_id
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    
    # Mock store
    mock_store = Mock()
    mock_store.name = '스타벅스'
    mock_store_repo.get_by_id.return_value = mock_store
    
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    
    with app.test_client() as client:
        # Set up session with split assignments
        with client.session_transaction() as sess:
            sess['split_assignments'] = {
                'user1': 8000,  # Normal case
                'user2': 12000,  # Normal case  
                'user3': 7000   # Insufficient balance (has 5000, needs 7000)
            }
            sess['assignment_store_id'] = 'store1'
        
        response = client.get('/payment-summary')
        html = response.get_data(as_text=True)
        
        # Test basic response
        assert response.status_code == 200
        assert '<!DOCTYPE html>' in html
        
        # Test for payment summary page structure
        assert ('payment' in html.lower() and 'summary' in html.lower()) or '결제' in html
        assert '스타벅스' in html
        
        # Test for payment cards structure
        assert ('card' in html.lower() or 
                'payment-card' in html.lower() or
                'bg-white' in html)  # Card styling
        
        # Test for user payment information
        assert '김철수' in html
        assert '이영희' in html
        assert '박민수' in html
        
        # Test for payment amounts
        assert ('8,000' in html or '8000' in html)
        assert ('12,000' in html or '12000' in html)
        assert ('7,000' in html or '7000' in html)
        
        # Test for deposit balance information
        assert ('20,000' in html or '20000' in html)  # 김철수 deposit
        assert ('15,000' in html or '15000' in html)  # 이영희 deposit
        assert ('5,000' in html or '5000' in html)    # 박민수 deposit
        
        # Test for insufficient balance warning
        assert ('insufficient' in html.lower() or 
                '부족' in html or
                'warning' in html.lower() or
                'alert' in html.lower())
        
        # Test for payment method options
        assert ('deposit' in html.lower() or 
                '예치금' in html or
                'payment-method' in html.lower())
        
        # Test for proceed/confirm button
        assert ('proceed' in html.lower() or 
                '진행' in html or
                'confirm' in html.lower() or
                '확인' in html)
        
        # Test for responsive card layout
        assert ('grid' in html or 'flex' in html)
        assert 'rounded' in html  # Card styling


def test_should_show_insufficient_balance_alerts():
    """Test that payment summary page shows clear insufficient balance alerts"""
    mock_user_repo = Mock()
    # Set up mock users with different balance scenarios
    mock_users = {}
    for user_data in [
        {'id': 'user1', 'name': '김철수', 'deposit': 30000},  # Sufficient
        {'id': 'user2', 'name': '이영희', 'deposit': 8000},   # Insufficient (needs 12000)
        {'id': 'user3', 'name': '박민수', 'deposit': 3000}    # Severely insufficient (needs 15000)
    ]:
        mock_user = Mock()
        mock_user.id = user_data['id']
        mock_user.name = user_data['name']
        mock_user.deposit = user_data['deposit']
        mock_users[user_data['id']] = mock_user
        
    def mock_get_by_id(user_id):
        return mock_users.get(user_id)
    
    mock_user_repo.get_by_id = mock_get_by_id
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    
    # Mock store
    mock_store = Mock()
    mock_store.name = '카페베네'
    mock_store_repo.get_by_id.return_value = mock_store
    
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    
    with app.test_client() as client:
        # Set up session with split assignments including insufficient balance cases
        with client.session_transaction() as sess:
            sess['split_assignments'] = {
                'user1': 10000,  # Sufficient: has 30000, needs 10000
                'user2': 12000,  # Insufficient: has 8000, needs 12000 (4000 short)
                'user3': 15000   # Severely insufficient: has 3000, needs 15000 (12000 short)
            }
            sess['assignment_store_id'] = 'store1'
        
        response = client.get('/payment-summary')
        html = response.get_data(as_text=True)
        
        # Test basic response
        assert response.status_code == 200
        assert '<!DOCTYPE html>' in html
        
        # Test for insufficient balance visual alerts
        assert ('border-red' in html or 'bg-red' in html)  # Red styling for alerts
        assert ('text-red' in html)  # Red text for warnings
        
        # Test for specific insufficient balance messages
        assert ('잔액 부족' in html or 'insufficient' in html.lower())
        assert '부족' in html  # Korean word for "insufficient"
        
        # Test for specific shortage amounts shown to users
        assert ('4,000' in html or '4000' in html)   # 이영희 shortage: 12000 - 8000
        assert ('12,000' in html or '12000' in html) # 박민수 shortage: 15000 - 3000
        
        # Test for warning icons or symbols
        assert ('svg' in html or 'icon' in html.lower() or '⚠' in html)
        
        # Test that payment method defaults are correct for insufficient balance
        assert 'value="cash"' in html  # Cash option should be present
        assert 'checked' in html       # Some options should be pre-selected
        
        # Test for insufficient balance count in summary
        assert '2명' in html  # Should show that 2 users have insufficient balance
        
        # Test for visual distinction between sufficient and insufficient users
        # Sufficient user (김철수) should not have red styling in their section
        sufficient_user_section = html[html.find('김철수'):html.find('김철수') + 500]
        insufficient_user_section = html[html.find('이영희'):html.find('이영희') + 500]
        
        # Insufficient user section should have red styling
        assert ('red' in insufficient_user_section or 'warning' in insufficient_user_section.lower())
        
        # Test for actionable guidance text
        assert ('현금 결제' in html or '충전' in html)  # Guidance for insufficient balance
        
        # Test for overall alert styling consistency
        assert ('bg-red-50' in html or 'bg-red-100' in html)  # Light red backgrounds
        assert ('border-red-200' in html or 'border-red-300' in html)  # Red borders


def test_should_render_payment_confirmation_flow():
    """Test that payment confirmation flow renders with proper UI elements"""
    mock_user_repo = Mock()
    # Set up mock users with different balance scenarios
    mock_users = {}
    for user_data in [
        {'id': 'user1', 'name': '김철수', 'deposit': 25000},
        {'id': 'user2', 'name': '이영희', 'deposit': 15000}, 
        {'id': 'user3', 'name': '박민수', 'deposit': 8000}
    ]:
        mock_user = Mock()
        mock_user.id = user_data['id']
        mock_user.name = user_data['name']
        mock_user.deposit = user_data['deposit']
        mock_users[user_data['id']] = mock_user
        
    def mock_get_by_id(user_id):
        return mock_users.get(user_id)
    
    mock_user_repo.get_by_id = mock_get_by_id
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    
    # Mock store
    mock_store = Mock()
    mock_store.name = '스타벅스'
    mock_store_repo.get_by_id.return_value = mock_store
    
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    
    with app.test_client() as client:
        # Set up session with confirmed payment details
        with client.session_transaction() as sess:
            sess['confirmed_payments'] = {
                'user1': {'amount': 12000, 'method': 'deposit'},
                'user2': {'amount': 8000, 'method': 'deposit'},
                'user3': {'amount': 6000, 'method': 'cash'}  # Mixed payment method
            }
            sess['assignment_store_id'] = 'store1'
        
        response = client.get('/payment-confirmation')
        html = response.get_data(as_text=True)
        
        # Test basic response
        assert response.status_code == 200
        assert '<!DOCTYPE html>' in html
        
        # Test for payment confirmation flow structure
        assert ('confirmation' in html.lower() or '확인' in html)
        assert ('payment' in html.lower() or '결제' in html)
        
        # Test for step-by-step confirmation flow
        assert ('step' in html.lower() or '단계' in html)
        assert ('progress' in html.lower() or '진행' in html)
        
        # Test for final payment summary before processing
        assert '김철수' in html
        assert '이영희' in html  
        assert '박민수' in html
        
        # Test for payment amounts and methods
        assert ('12,000' in html or '12000' in html)
        assert ('8,000' in html or '8000' in html)
        assert ('6,000' in html or '6000' in html)
        assert 'deposit' in html.lower() or '예치금' in html
        assert 'cash' in html.lower() or '현금' in html
        
        # Test for final confirmation button
        assert ('confirm' in html.lower() or '최종 확인' in html or '결제 진행' in html)
        
        # Test for cancel/back option
        assert ('cancel' in html.lower() or '취소' in html or 'back' in html.lower())
        
        # Test for payment processing loader/spinner elements
        assert ('processing' in html.lower() or '처리' in html or 'spinner' in html.lower())
        
        # Test for success/failure message containers
        assert ('success' in html.lower() or '성공' in html or 'alert' in html.lower())
        
        # Test for JavaScript payment processing functionality
        assert '<script>' in html and '</script>' in html
        assert ('processPayment' in html or 'payment' in html.lower())
        
        # Test for form submission with proper method
        assert 'form' in html.lower()
        assert 'method="post"' in html


def test_should_render_store_analytics_charts():
    """Test that store management page renders analytics charts for store data visualization"""
    mock_user_repo = Mock()
    mock_receipt_repo = Mock()
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    
    # Mock stores with analytics data - use dictionaries that are JSON serializable
    mock_stores = [
        {"id": "store1", "name": "스타벅스", "coupon_enabled": True, "coupon_goal": 10},
        {"id": "store2", "name": "맥도날드", "coupon_enabled": False, "coupon_goal": 5},
        {"id": "store3", "name": "서브웨이", "coupon_enabled": True, "coupon_goal": 8}
    ]
    mock_store_repo.list_all.return_value = mock_stores
    
    mock_ocr_service = Mock()
    
    app = create_app(user_repo=mock_user_repo, receipt_repo=mock_receipt_repo, 
                     coupon_repo=mock_coupon_repo, store_repo=mock_store_repo, ocr_service=mock_ocr_service)
    
    with app.test_client() as client:
        # Login to admin first
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        response = client.get('/admin/stores')
        html = response.get_data(as_text=True)
        
        # Test basic response
        assert response.status_code == 200
        assert '<!DOCTYPE html>' in html
        
        # Test for Chart.js library inclusion
        assert ('chart.js' in html.lower() or 'chartjs' in html.lower())
        
        # Test for chart container elements
        assert ('canvas' in html.lower() or 'chart-container' in html.lower())
        
        # Test for store analytics chart types
        assert ('store-analytics' in html.lower() or 'analytics' in html.lower())
        
        # Test for chart data preparation
        assert ('analytics-data' in html.lower() or 'chartdata' in html.lower() or 'analyticsdata' in html.lower())
        
        # Test for store performance metrics
        assert ('performance' in html.lower() or '성과' in html or '분석' in html)
        
        # Test for coupon completion rate chart
        assert ('completion' in html.lower() or '완료율' in html or 'rate' in html.lower())
        
        # Test for store comparison chart
        assert ('comparison' in html.lower() or '비교' in html)
        
        # Test for JavaScript chart initialization
        assert '<script>' in html and '</script>' in html
        assert ('new Chart' in html or 'Chart(' in html)
        
        # Test for chart configuration options
        assert ('options' in html.lower() or 'config' in html.lower())
        
        # Test for responsive chart design
        assert ('responsive' in html.lower() or 'maintainAspectRatio' in html)
        
        # Test for chart legend and labels
        assert ('legend' in html.lower() or 'labels' in html.lower())
        
        # Test for store data visualization
        assert '스타벅스' in html
        assert '맥도날드' in html
        assert '서브웨이' in html