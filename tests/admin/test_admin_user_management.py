import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from src.web.app import create_app


class TestAdminUserManagement:
    
    @pytest.fixture
    def client(self):
        self.user_repo = Mock()
        receipt_repo = Mock()
        coupon_repo = Mock()
        ocr_service = Mock()
        store_repo = Mock()
        coupon_service = Mock()
        
        app = create_app(
            user_repo=self.user_repo,
            receipt_repo=receipt_repo,
            coupon_repo=coupon_repo,
            ocr_service=ocr_service,
            store_repo=store_repo,
            coupon_service=coupon_service
        )
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_should_display_all_users_in_admin(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        user1 = Mock()
        user1.name = 'User1'
        user1.deposit = Decimal('100.0')
        user2 = Mock()
        user2.name = 'User2'
        user2.deposit = Decimal('200.0')
        self.user_repo.list_all.return_value = [user1, user2]
        
        response = client.get('/admin/users')
        assert response.status_code == 200
        content = response.get_data(as_text=True)
        assert 'User1' in content
        assert 'User2' in content
        assert '100.0' in content
        assert '200.0' in content
    
    def test_should_allow_admin_to_create_user(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        response = client.post('/admin/users', data={
            'name': 'New User',
            'deposit': '500.0'
        })
        assert response.status_code == 302
        self.user_repo.save.assert_called_once()
    
    def test_should_allow_admin_to_add_deposit(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
            
        user = Mock()
        user.deposit = Decimal('100.0')
        self.user_repo.get_by_id.return_value = user
        
        response = client.post('/admin/users/user1/add-deposit', data={
            'amount': '50.0'
        })
        assert response.status_code == 302
        user.add_deposit.assert_called_once_with(Decimal('50.0'))
        self.user_repo.save.assert_called_once_with(user)
    
    def test_should_allow_admin_to_delete_user(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
            
        response = client.post('/admin/users/user1/delete')
        assert response.status_code == 302
        self.user_repo.delete.assert_called_once_with('user1')