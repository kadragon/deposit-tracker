import pytest
from flask import Flask
from src.web.app import app
from unittest.mock import Mock, patch


def test_should_display_user_selection_page():
    with patch('src.web.app.UserRepository') as mock_user_repo_class:
        mock_user_repo = Mock()
        mock_user_repo_class.return_value = mock_user_repo
        mock_user_repo.list_all.return_value = []
        
        client = app.test_client()
        response = client.get('/')
        
        assert response.status_code == 200
        assert 'user-selection' in response.get_data(as_text=True)


def test_should_list_all_available_users():
    with patch('src.web.app.UserRepository') as mock_user_repo_class:
        mock_user_repo = Mock()
        mock_user_repo_class.return_value = mock_user_repo
        mock_user_repo.list_all.return_value = [
            Mock(name="홍길동", id="user1"),
            Mock(name="김철수", id="user2")
        ]
        
        client = app.test_client()
        response = client.get('/')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert "홍길동" in response_text
        assert "김철수" in response_text


def test_should_redirect_to_dashboard_when_user_selected():
    with patch('src.web.app.UserRepository') as mock_user_repo_class:
        mock_user_repo = Mock()
        mock_user_repo_class.return_value = mock_user_repo
        mock_user_repo.list_all.return_value = []
        
        client = app.test_client()
        response = client.post('/', data={'user_id': 'user123'})
        
        assert response.status_code == 302
        assert '/dashboard/user123' in response.location
