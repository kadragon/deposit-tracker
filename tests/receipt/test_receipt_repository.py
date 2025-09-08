import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.models.user import User
from src.models.store import Store
from src.models.receipt import Receipt
from src.models.receipt_item import ReceiptItem
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
        
        # Verify the actual data content being saved
        from google.cloud import firestore
        
        call_args, _ = mock_collection.add.call_args
        saved_data = call_args[0]
        
        assert saved_data["user_id"] == "user123"
        assert saved_data["store_id"] == "store123"
        assert saved_data["total"] == "4000"  # Should be string for precision
        assert len(saved_data["items"]) == 1
        assert saved_data["items"][0]["name"] == "사과"
        assert saved_data["items"][0]["price"] == "2000"  # Should be string for precision
        assert saved_data["items"][0]["quantity"] == 2
        assert saved_data["created_at"] == firestore.SERVER_TIMESTAMP


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


def test_should_save_receipt_with_user_assignments():
    # Mock Firestore
    mock_db = Mock()
    mock_collection = Mock()
    mock_doc_ref = Mock()
    mock_db.collection.return_value = mock_collection
    mock_collection.add.return_value = (mock_doc_ref, None)
    mock_doc_ref.id = "receipt123"
    
    with patch('google.cloud.firestore.Client', return_value=mock_db):
        repository = ReceiptRepository()
        
        # Create users
        user1 = User(name="홍길동", deposit=10000)
        user1.id = "user1"
        user2 = User(name="김영희", deposit=10000) 
        user2.id = "user2"
        user3 = User(name="박철수", deposit=10000)
        user3.id = "user3"
        
        # Create store
        store = Store(name="스타벅스")
        store.id = "store123"
        
        # Create receipt with multiple participants
        receipt = Receipt(user=user1, store=store)
        receipt.add_participant(user2)
        receipt.add_participant(user3)
        
        # Add items with different user assignments
        item1 = ReceiptItem("아메리카노", 4500)
        item1.assign_to_user(user1)  # Individual item
        
        item2 = ReceiptItem("치즈케이크", 6200)
        item2.assign_to_user(user1)  # Shared item
        item2.assign_to_user(user2)
        
        item3 = ReceiptItem("라떼", 5000)
        item3.assign_to_user(user3)  # Individual item
        
        receipt.add_receipt_item(item1)
        receipt.add_receipt_item(item2)
        receipt.add_receipt_item(item3)
        
        receipt_id = repository.save(receipt)
        
        assert receipt_id == "receipt123"
        mock_db.collection.assert_called_with("receipts")
        mock_collection.add.assert_called_once()
        
        # Verify the assignment data is saved
        from google.cloud import firestore
        
        call_args, _ = mock_collection.add.call_args
        saved_data = call_args[0]
        
        # Check basic receipt data
        assert saved_data["user_id"] == "user1"  # uploader
        assert saved_data["store_id"] == "store123"
        
        # Check participant data  
        assert "participants" in saved_data
        assert len(saved_data["participants"]) == 2  # user2, user3
        assert "user2" in saved_data["participants"]
        assert "user3" in saved_data["participants"]
        
        # Check items with user assignments
        assert len(saved_data["items"]) == 3
        
        # Item 1 - assigned to user1 only
        item1_data = saved_data["items"][0]
        assert item1_data["name"] == "아메리카노"
        assert item1_data["assigned_users"] == ["user1"]
        
        # Item 2 - shared between user1 and user2
        item2_data = saved_data["items"][1] 
        assert item2_data["name"] == "치즈케이크"
        assert set(item2_data["assigned_users"]) == {"user1", "user2"}
        
        # Item 3 - assigned to user3 only
        item3_data = saved_data["items"][2]
        assert item3_data["name"] == "라떼"
        assert item3_data["assigned_users"] == ["user3"]


def test_should_retrieve_receipts_by_uploader():
    # Mock Firestore
    mock_db = Mock()
    mock_collection = Mock()
    mock_query = Mock()
    mock_docs = [
        Mock(id="receipt1", to_dict=Mock(return_value={
            "user_id": "uploader1",  # uploader
            "store_id": "store123",
            "participants": ["user2", "user3"],
            "items": [{"name": "커피", "price": "4000", "quantity": 1, "assigned_users": ["uploader1"]}],
            "total": "4000"
        })),
        Mock(id="receipt2", to_dict=Mock(return_value={
            "user_id": "uploader1",  # same uploader
            "store_id": "store456",
            "participants": ["user4"],
            "items": [{"name": "케이크", "price": "6000", "quantity": 1, "assigned_users": ["user4"]}],
            "total": "6000"
        }))
    ]
    
    mock_db.collection.return_value = mock_collection
    mock_collection.where.return_value = mock_query
    mock_query.get.return_value = mock_docs
    
    with patch('google.cloud.firestore.Client', return_value=mock_db):
        repository = ReceiptRepository()
        
        receipts = repository.find_by_uploader("uploader1")
        
        assert len(receipts) == 2
        assert receipts[0]["id"] == "receipt1"
        assert receipts[0]["user_id"] == "uploader1"
        assert receipts[0]["participants"] == ["user2", "user3"]
        assert receipts[1]["id"] == "receipt2"
        assert receipts[1]["user_id"] == "uploader1"
        assert receipts[1]["participants"] == ["user4"]
        
        mock_db.collection.assert_called_with("receipts")
        mock_collection.where.assert_called_with("user_id", "==", "uploader1")


def test_should_retrieve_split_transactions_by_user():
    # Mock Firestore
    mock_db = Mock()
    mock_collection = Mock()
    mock_query = Mock()
    mock_docs = [
        Mock(id="receipt1", to_dict=Mock(return_value={
            "user_id": "uploader1",
            "store_id": "store123", 
            "participants": ["user1", "user2"],
            "items": [
                {"name": "커피", "price": "4000", "quantity": 1, "assigned_users": ["user1"]},
                {"name": "케이크", "price": "6000", "quantity": 1, "assigned_users": ["user1", "user2"]}
            ],
            "total": "10000",
            "split_transactions": {
                "user1": "7000",  # 4000 + 3000 (half of shared cake)
                "user2": "3000"   # 3000 (half of shared cake)
            }
        })),
        Mock(id="receipt2", to_dict=Mock(return_value={
            "user_id": "uploader2",
            "store_id": "store456",
            "participants": ["user1", "user3"],
            "items": [{"name": "라떼", "price": "5000", "quantity": 1, "assigned_users": ["user1"]}],
            "total": "5000",
            "split_transactions": {
                "user1": "5000"
            }
        }))
    ]
    
    mock_db.collection.return_value = mock_collection
    mock_collection.where.return_value = mock_query
    mock_query.get.return_value = mock_docs
    
    with patch('google.cloud.firestore.Client', return_value=mock_db):
        repository = ReceiptRepository()
        
        transactions = repository.find_split_transactions_by_user("user1")
        
        assert len(transactions) == 2
        
        # First transaction: user1 paid 7000 in receipt1
        assert transactions[0]["receipt_id"] == "receipt1"
        assert transactions[0]["user_amount"] == "7000"
        assert transactions[0]["total_amount"] == "10000"
        
        # Second transaction: user1 paid 5000 in receipt2  
        assert transactions[1]["receipt_id"] == "receipt2"
        assert transactions[1]["user_amount"] == "5000"
        assert transactions[1]["total_amount"] == "5000"
        
        mock_db.collection.assert_called_with("receipts")
        # Should query for receipts where user1 is in split_transactions
        mock_collection.where.assert_called_with("split_transactions.user1", ">=", "")