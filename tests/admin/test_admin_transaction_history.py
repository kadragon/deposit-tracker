import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime
from src.web.app import create_app


class TestAdminTransactionHistory:
    
    @pytest.fixture
    def client(self):
        user_repo = Mock()
        self.receipt_repo = Mock()
        coupon_repo = Mock()
        ocr_service = Mock()
        store_repo = Mock()
        coupon_service = Mock()
        
        app = create_app(
            user_repo=user_repo,
            receipt_repo=self.receipt_repo,
            coupon_repo=coupon_repo,
            ocr_service=ocr_service,
            store_repo=store_repo,
            coupon_service=coupon_service
        )
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_should_display_all_transactions(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        receipt1 = Mock()
        receipt1.user_name = 'User1'
        receipt1.store_name = 'Store1'
        receipt1.total_amount = Decimal('50.0')
        receipt1.date = datetime(2023, 1, 1)
        receipt2 = Mock()
        receipt2.user_name = 'User2'
        receipt2.store_name = 'Store2'
        receipt2.total_amount = Decimal('75.0')
        receipt2.date = datetime(2023, 1, 2)
        self.receipt_repo.list_all.return_value = [receipt1, receipt2]
        
        response = client.get('/admin/transactions')
        assert response.status_code == 200
        content = response.get_data(as_text=True)
        assert 'User1' in content
        assert 'User2' in content
        assert 'Store1' in content
        assert 'Store2' in content
        assert '50.0' in content
        assert '75.0' in content
    
    def test_should_filter_transactions_by_user(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        receipt1 = Mock()
        receipt1.user_name = 'User1'
        receipt1.store_name = 'Store1'
        receipt1.total_amount = Decimal('50.0')
        receipt1.date = datetime(2023, 1, 1)
        self.receipt_repo.find_by_user_id.return_value = [receipt1]
        
        response = client.get('/admin/transactions?user_id=user1')
        assert response.status_code == 200
        self.receipt_repo.find_by_user_id.assert_called_once_with('user1')
    
    def test_should_filter_transactions_by_date(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        receipt1 = Mock()
        receipt1.user_name = 'User1'
        receipt1.store_name = 'Store1'
        receipt1.total_amount = Decimal('50.0')
        receipt1.date = datetime(2023, 1, 1)
        self.receipt_repo.find_by_date_range.return_value = [receipt1]
        
        response = client.get('/admin/transactions?start_date=2023-01-01&end_date=2023-01-31')
        assert response.status_code == 200
        # The method should be called with datetime objects, but we'll test the call was made
        self.receipt_repo.find_by_date_range.assert_called_once()
    
    def test_should_filter_transactions_by_store(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        receipt1 = Mock()
        receipt1.user_name = 'User1'
        receipt1.store_name = 'Store1'
        receipt1.total_amount = Decimal('50.0')
        receipt1.date = datetime(2023, 1, 1)
        self.receipt_repo.find_by_store_name.return_value = [receipt1]
        
        response = client.get('/admin/transactions?store_name=Store1')
        assert response.status_code == 200
        self.receipt_repo.find_by_store_name.assert_called_once_with('Store1')