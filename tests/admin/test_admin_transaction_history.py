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
    
    def test_should_display_split_payment_details(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        # Mock split payment receipt with multiple users
        receipt = Mock()
        receipt.id = 'receipt123'
        receipt.user_name = 'User1'
        receipt.store_name = 'Store1'
        receipt.total_amount = Decimal('100.0')
        receipt.date = datetime(2023, 1, 1)
        receipt.is_split_payment = True
        
        # Mock split details
        split_detail1 = Mock()
        split_detail1.user_name = 'User1'
        split_detail1.amount = Decimal('40.0')
        split_detail1.payment_method = 'deposit'
        
        split_detail2 = Mock()
        split_detail2.user_name = 'User2'
        split_detail2.amount = Decimal('60.0')
        split_detail2.payment_method = 'deposit'
        
        self.receipt_repo.get_by_id.return_value = receipt
        self.receipt_repo.get_split_payment_details.return_value = [split_detail1, split_detail2]
        
        response = client.get('/admin/transactions/receipt123/split-details')
        assert response.status_code == 200
        content = response.get_data(as_text=True)
        
        # Check split payment details are displayed
        assert 'User1' in content
        assert 'User2' in content
        assert '40.0' in content
        assert '60.0' in content
        assert 'deposit' in content
        assert 'split-payment-details' in content
        
        self.receipt_repo.get_split_payment_details.assert_called_once_with('receipt123')
    
    def test_should_show_receipt_uploader_vs_payers(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        # Mock receipt with uploader different from payers
        receipt = Mock()
        receipt.id = 'receipt456'
        receipt.user_name = 'User1'  # The uploader
        receipt.store_name = 'Store1'
        receipt.total_amount = Decimal('80.0')
        receipt.date = datetime(2023, 1, 1)
        
        # Mock payers information
        payers_info = [
            {'user_name': 'User2', 'amount': Decimal('30.0')},
            {'user_name': 'User3', 'amount': Decimal('50.0')}
        ]
        
        self.receipt_repo.get_by_id.return_value = receipt
        self.receipt_repo.get_payers_info.return_value = payers_info
        
        response = client.get('/admin/transactions/receipt456/uploader-vs-payers')
        assert response.status_code == 200
        content = response.get_data(as_text=True)
        
        # Check uploader vs payers distinction is displayed
        assert 'uploader-payers-info' in content
        assert 'User1' in content  # uploader
        assert 'User2' in content  # payer
        assert 'User3' in content  # payer
        assert '30.0' in content   # payer amount
        assert '50.0' in content   # payer amount
        
        self.receipt_repo.get_payers_info.assert_called_once_with('receipt456')
    
    def test_should_export_detailed_financial_report(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        # Mock financial report data
        report_data = {
            'total_transactions': 5,
            'total_amount': Decimal('500.0'),
            'deposit_payments': Decimal('300.0'),
            'cash_payments': Decimal('200.0'),
            'by_user': [
                {'user_name': 'User1', 'total_spent': Decimal('200.0'), 'deposit_used': Decimal('150.0')},
                {'user_name': 'User2', 'total_spent': Decimal('300.0'), 'deposit_used': Decimal('150.0')}
            ],
            'by_store': [
                {'store_name': 'Store1', 'total_amount': Decimal('300.0'), 'transaction_count': 3},
                {'store_name': 'Store2', 'total_amount': Decimal('200.0'), 'transaction_count': 2}
            ]
        }
        
        self.receipt_repo.generate_financial_report.return_value = report_data
        
        response = client.get('/admin/transactions/financial-report?format=json', headers={'Accept': 'application/json'})
        assert response.status_code == 200
        
        # Parse JSON response to properly test JSON endpoint
        data = response.get_json()
        assert data is not None
        assert data['total_transactions'] == 5
        assert data['total_amount'] == '500.0'  # Should be serialized as string
        assert data['deposit_payments'] == '300.0'
        assert data['cash_payments'] == '200.0'
        assert len(data['by_user']) == 2
        assert data['by_user'][0]['user_name'] == 'User1'
        assert data['by_user'][0]['total_spent'] == '200.0'
        assert len(data['by_store']) == 2
        assert data['by_store'][0]['store_name'] == 'Store1'
        
        self.receipt_repo.generate_financial_report.assert_called_once()