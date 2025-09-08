import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from src.web.app import create_app


class TestAdminStoreManagement:
    
    @pytest.fixture
    def client(self):
        user_repo = Mock()
        receipt_repo = Mock()
        coupon_repo = Mock()
        ocr_service = Mock()
        self.store_repo = Mock()
        coupon_service = Mock()
        
        app = create_app(
            user_repo=user_repo,
            receipt_repo=receipt_repo,
            coupon_repo=coupon_repo,
            ocr_service=ocr_service,
            store_repo=self.store_repo,
            coupon_service=coupon_service
        )
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_should_display_all_stores_in_admin(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        store1 = Mock()
        store1.name = 'Store1'
        store1.coupon_enabled = True
        store1.coupon_goal = 10
        store2 = Mock()
        store2.name = 'Store2'
        store2.coupon_enabled = False
        store2.coupon_goal = 5
        self.store_repo.list_all.return_value = [store1, store2]
        
        response = client.get('/admin/stores')
        assert response.status_code == 200
        content = response.get_data(as_text=True)
        assert 'Store1' in content
        assert 'Store2' in content
        assert '활성화' in content
        assert '비활성화' in content
    
    def test_should_allow_admin_to_create_store(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
        
        response = client.post('/admin/stores', data={
            'name': 'New Store',
            'coupon_enabled': 'on',
            'coupon_goal': '8'
        })
        assert response.status_code == 302
        self.store_repo.save.assert_called_once()
    
    def test_should_allow_admin_to_toggle_coupon_system(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
            
        store = Mock()
        store.coupon_enabled = True
        self.store_repo.get_by_id.return_value = store
        
        response = client.post('/admin/stores/store1/toggle-coupon')
        assert response.status_code == 302
        assert store.coupon_enabled == False
        self.store_repo.save.assert_called_once_with(store)
    
    def test_should_allow_admin_to_set_coupon_goal(self, client):
        # Log in as admin
        with client.session_transaction() as sess:
            sess['admin_logged_in'] = True
            
        store = Mock()
        store.coupon_goal = 10
        self.store_repo.get_by_id.return_value = store
        
        response = client.post('/admin/stores/store1/set-goal', data={
            'goal': '15'
        })
        assert response.status_code == 302
        assert store.coupon_goal == 15
        self.store_repo.save.assert_called_once_with(store)