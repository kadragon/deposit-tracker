import pytest
from unittest.mock import Mock
from src.models.store import Store
from src.repositories.store_repository import StoreRepository


def test_should_save_store_to_firestore():
    # Arrange
    mock_firestore = Mock()
    mock_collection = mock_firestore.collection.return_value
    mock_doc_ref = Mock()
    mock_doc_ref.id = "generated_store_id"
    mock_collection.add.return_value = (None, mock_doc_ref)
    
    repository = StoreRepository(mock_firestore)
    store = Store(name="편의점A")
    
    # Act
    result = repository.save(store)
    
    # Assert
    mock_firestore.collection.assert_called_once_with("stores")
    expected_data = {
        "name": "편의점A",
        "coupon_enabled": False,
        "coupon_goal": 0,
    }
    mock_collection.add.assert_called_once_with(expected_data)
    assert result == "generated_store_id"


def test_should_retrieve_store_by_id():
    # Arrange
    mock_firestore = Mock()
    mock_doc_ref = Mock()
    mock_doc = Mock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "name": "편의점A", 
        "coupon_enabled": True, 
        "coupon_goal": 10
    }
    mock_doc_ref.get.return_value = mock_doc
    mock_firestore.collection.return_value.document.return_value = mock_doc_ref
    
    repository = StoreRepository(mock_firestore)
    
    # Act
    store = repository.get_by_id("store123")
    
    # Assert
    mock_firestore.collection.assert_called_with("stores")
    mock_firestore.collection.return_value.document.assert_called_with("store123")
    assert store.name == "편의점A"
    assert store.coupon_enabled is True
    assert store.coupon_goal == 10


def test_should_find_store_by_name():
    # Arrange
    mock_firestore = Mock()
    mock_doc = Mock()
    mock_doc.to_dict.return_value = {
        "name": "편의점A",
        "coupon_enabled": False,
        "coupon_goal": 0
    }
    
    mock_firestore.collection.return_value.where.return_value.limit.return_value.stream.return_value = [mock_doc]
    
    repository = StoreRepository(mock_firestore)
    
    # Act
    store = repository.find_by_name("편의점A")
    
    # Assert
    mock_firestore.collection.assert_called_with("stores")
    mock_firestore.collection.return_value.where.assert_called_with("name", "==", "편의점A")
    assert store.name == "편의점A"
    assert store.coupon_enabled is False
    assert store.coupon_goal == 0