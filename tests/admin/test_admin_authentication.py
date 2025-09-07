import pytest
from unittest.mock import Mock, patch
from src.web.app import create_app


class TestAdminAuthentication:
    
    @pytest.fixture
    def client(self):
        user_repo = Mock()
        receipt_repo = Mock()
        coupon_repo = Mock()
        ocr_service = Mock()
        store_repo = Mock()
        coupon_service = Mock()
        
        app = create_app(
            user_repo=user_repo,
            receipt_repo=receipt_repo,
            coupon_repo=coupon_repo,
            ocr_service=ocr_service,
            store_repo=store_repo,
            coupon_service=coupon_service
        )
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_should_require_admin_login(self, client):
        response = client.get('/admin')
        assert response.status_code == 302
        assert '/admin/login' in response.headers['Location']
    
    def test_should_validate_admin_credentials(self, client):
        response = client.post('/admin/login', data={
            'username': 'admin',
            'password': 'password'
        })
        assert response.status_code == 302
        assert '/admin' in response.headers['Location']
    
    def test_should_restrict_access_to_admin_pages(self, client):
        response = client.get('/admin/users')
        assert response.status_code == 302
        assert '/admin/login' in response.headers['Location']