import pytest
from unittest.mock import Mock
from src.models.coupon import Coupon
from src.repositories.coupon_repository import CouponRepository


def test_should_save_coupon_to_firestore():
    # Arrange
    mock_firestore = Mock()
    mock_collection = mock_firestore.collection.return_value
    mock_doc_ref = Mock()
    mock_doc_ref.id = "generated_coupon_id"
    # Firestore add returns (DocumentReference, WriteResult)
    mock_collection.add.return_value = (mock_doc_ref, Mock())

    repository = CouponRepository(mock_firestore)
    coupon = Coupon(user_id="user123", store_id="store456", count=5)
    
    # Act
    result = repository.save(coupon)
    
    # Assert
    mock_firestore.collection.assert_called_once_with("coupons")
    expected_data = {"user_id": "user123", "store_id": "store456", "count": 5}
    mock_collection.add.assert_called_once_with(expected_data)
    assert result == "generated_coupon_id"


def test_should_retrieve_coupons_by_user():
    # Arrange
    mock_firestore = Mock()
    mock_collection = mock_firestore.collection.return_value
    mock_query = mock_collection.where.return_value
    
    # Mock firestore document
    mock_doc = Mock()
    mock_doc.to_dict.return_value = {"user_id": "user123", "store_id": "store456", "count": 3}
    mock_query.stream.return_value = [mock_doc]
    
    repository = CouponRepository(mock_firestore)
    
    # Act
    coupons = repository.get_by_user("user123")
    
    # Assert
    mock_firestore.collection.assert_called_once_with("coupons")
    mock_collection.where.assert_called_once_with("user_id", "==", "user123")
    mock_query.stream.assert_called_once()
    assert len(coupons) == 1
    assert coupons[0].user_id == "user123"
    assert coupons[0].store_id == "store456"
    assert coupons[0].count == 3


def test_should_update_coupon_count():
    # Arrange
    mock_firestore = Mock()
    mock_collection = mock_firestore.collection.return_value
    
    # Mock existing coupon document
    mock_doc = Mock()
    mock_doc.id = "coupon_doc_id"
    mock_collection.where.return_value.where.return_value.limit.return_value.stream.return_value = [mock_doc]
    
    repository = CouponRepository(mock_firestore)
    
    # Act
    repository.update_count("user123", "store456", 8)
    
    # Assert - Just verify the key calls without detailed mock verification
    # The important thing is that update is called with the right count
    mock_collection.document.return_value.update.assert_called_once_with({"count": 8})


def test_get_by_user_and_store_returns_new_coupon_when_missing():
    # Arrange
    mock_firestore = Mock()
    mock_collection = mock_firestore.collection.return_value
    # No existing coupon
    mock_collection.where.return_value.where.return_value.limit.return_value.stream.return_value = []

    repo = CouponRepository(mock_firestore)

    # Act
    coupon = repo.get_by_user_and_store("u1", "s1")

    # Assert: returns a new coupon with count 0
    assert isinstance(coupon, Coupon)
    assert coupon.user_id == "u1"
    assert coupon.store_id == "s1"
    assert coupon.count == 0


def test_update_count_creates_when_missing():
    # Arrange
    mock_firestore = Mock()
    mock_collection = mock_firestore.collection.return_value
    # No existing matching document
    mock_collection.where.return_value.where.return_value.limit.return_value.stream.return_value = []
    
    # Mock the add method to return a tuple (DocumentReference, WriteResult)
    mock_doc_ref = Mock()
    mock_doc_ref.id = "new_doc_id"
    mock_collection.add.return_value = (mock_doc_ref, Mock())

    repo = CouponRepository(mock_firestore)

    # Act
    repo.update_count("u2", "s2", 5)

    # Assert: falls back to creating a new coupon via add
    expected_data = {"user_id": "u2", "store_id": "s2", "count": 5}
    mock_collection.add.assert_called_once_with(expected_data)
