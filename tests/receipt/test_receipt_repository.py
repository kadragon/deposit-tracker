import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.models.user import User
from src.models.store import Store
from src.models.receipt import Receipt
from src.repositories.receipt_repository import ReceiptRepository


def test_should_save_receipt_to_firestore():
    # Mock Firestore
    mock_db = Mock()
    mock_collection = Mock()
    mock_doc_ref = Mock()
    mock_db.collection.return_value = mock_collection
    mock_collection.add.return_value = (mock_doc_ref, None)
    mock_doc_ref.id = "receipt123"
    
    with patch('google.cloud.firestore.Client', return_value=mock_db):
        repository = ReceiptRepository()
        
        user = User(name="홍길동", deposit=10000)
        user.id = "user123"
        store = Store(name="이마트")  
        store.id = "store123"
        receipt = Receipt(user=user, store=store)
        receipt.add_item("사과", 2000, 2)
        
        receipt_id = repository.save(receipt)
        
        assert receipt_id == "receipt123"
        mock_db.collection.assert_called_with("receipts")
        mock_collection.add.assert_called_once()


def test_should_retrieve_receipts_by_user():
    # Mock Firestore
    mock_db = Mock()
    mock_collection = Mock()
    mock_query = Mock()
    mock_docs = [
        Mock(id="receipt1", to_dict=Mock(return_value={
            "user_id": "user123",
            "store_id": "store123", 
            "items": [{"name": "사과", "price": 2000, "quantity": 2}],
            "total": 4000
        })),
        Mock(id="receipt2", to_dict=Mock(return_value={
            "user_id": "user123",
            "store_id": "store456",
            "items": [{"name": "바나나", "price": 3000, "quantity": 1}],
            "total": 3000
        }))
    ]
    
    mock_db.collection.return_value = mock_collection
    mock_collection.where.return_value = mock_query
    mock_query.get.return_value = mock_docs
    
    with patch('google.cloud.firestore.Client', return_value=mock_db):
        repository = ReceiptRepository()
        
        receipts = repository.find_by_user_id("user123")
        
        assert len(receipts) == 2
        assert receipts[0]["id"] == "receipt1"
        assert receipts[0]["user_id"] == "user123" 
        assert receipts[0]["total"] == 4000
        assert receipts[1]["id"] == "receipt2"
        assert receipts[1]["total"] == 3000
        
        mock_db.collection.assert_called_with("receipts")
        mock_collection.where.assert_called_with("user_id", "==", "user123")


def test_should_retrieve_receipts_by_date_range():
    # Mock Firestore
    mock_db = Mock()
    mock_collection = Mock()
    mock_query = Mock()
    mock_query2 = Mock()
    mock_docs = [
        Mock(id="receipt1", to_dict=Mock(return_value={
            "user_id": "user123",
            "store_id": "store123",
            "items": [{"name": "사과", "price": 2000, "quantity": 2}],
            "total": 4000,
            "created_at": datetime(2024, 1, 15)
        }))
    ]
    
    mock_db.collection.return_value = mock_collection
    mock_collection.where.return_value = mock_query
    mock_query.where.return_value = mock_query2
    mock_query2.get.return_value = mock_docs
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    
    with patch('google.cloud.firestore.Client', return_value=mock_db):
        repository = ReceiptRepository()
        
        receipts = repository.find_by_date_range(start_date, end_date)
        
        assert len(receipts) == 1
        assert receipts[0]["id"] == "receipt1"
        assert receipts[0]["total"] == 4000
        
        mock_db.collection.assert_called_with("receipts")
        mock_collection.where.assert_called_with("created_at", ">=", start_date)
        mock_query.where.assert_called_with("created_at", "<=", end_date)