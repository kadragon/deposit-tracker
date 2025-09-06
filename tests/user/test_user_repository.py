import pytest
from unittest.mock import Mock, patch
from src.models.user import User
from src.repositories.user_repository import UserRepository


def test_should_save_user_to_firestore():
    # Arrange
    mock_firestore = Mock()
    mock_collection = mock_firestore.collection.return_value
    repository = UserRepository(mock_firestore)
    user = User(name="홍길동", deposit=25000)
    
    # Act
    result = repository.save(user)
    
    # Assert
    mock_firestore.collection.assert_called_once_with("users")
    expected_data = {"name": "홍길동", "deposit": 25000}
    mock_collection.add.assert_called_once_with(expected_data)
    assert result is not None


def test_should_retrieve_user_by_id():
    # Arrange
    mock_firestore = Mock()
    mock_doc_ref = Mock()
    mock_doc = Mock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"name": "홍길동", "deposit": 25000}
    mock_doc_ref.get.return_value = mock_doc
    mock_firestore.collection.return_value.document.return_value = mock_doc_ref
    
    repository = UserRepository(mock_firestore)
    
    # Act
    user = repository.get_by_id("user123")
    
    # Assert
    mock_firestore.collection.assert_called_with("users")
    mock_firestore.collection.return_value.document.assert_called_with("user123")
    assert user.name == "홍길동"
    assert user.deposit == 25000


def test_should_list_all_users():
    # Arrange
    mock_firestore = Mock()
    mock_doc1 = Mock()
    mock_doc1.to_dict.return_value = {"name": "홍길동", "deposit": 25000}
    mock_doc2 = Mock()
    mock_doc2.to_dict.return_value = {"name": "김철수", "deposit": 15000}
    
    mock_firestore.collection.return_value.stream.return_value = [mock_doc1, mock_doc2]
    
    repository = UserRepository(mock_firestore)
    
    # Act
    users = repository.list_all()
    
    # Assert
    mock_firestore.collection.assert_called_with("users")
    assert len(users) == 2
    assert users[0].name == "홍길동"
    assert users[0].deposit == 25000
    assert users[1].name == "김철수"
    assert users[1].deposit == 15000