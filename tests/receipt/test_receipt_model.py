import pytest
from src.models.user import User
from src.models.store import Store
from src.models.receipt import Receipt


def test_should_create_receipt_with_user_and_store():
    user = User(name="홍길동", deposit=25000)
    store = Store(name="이마트")
    
    receipt = Receipt(user=user, store=store)
    
    assert receipt.user == user
    assert receipt.store == store


def test_should_add_items_to_receipt():
    user = User(name="홍길동", deposit=25000)
    store = Store(name="이마트")
    receipt = Receipt(user=user, store=store)
    
    receipt.add_item("사과", 2000, 2)
    receipt.add_item("바나나", 3000, 1)
    
    assert len(receipt.items) == 2
    assert receipt.items[0].name == "사과"
    assert receipt.items[0].price == 2000
    assert receipt.items[0].quantity == 2
    assert receipt.items[1].name == "바나나"
    assert receipt.items[1].price == 3000
    assert receipt.items[1].quantity == 1


def test_should_calculate_total_amount():
    user = User(name="홍길동", deposit=25000)
    store = Store(name="이마트")
    receipt = Receipt(user=user, store=store)
    
    receipt.add_item("사과", 2000, 2)  # 4000
    receipt.add_item("바나나", 3000, 1)  # 3000
    receipt.add_item("우유", 1500, 3)  # 4500
    
    total = receipt.calculate_total()
    
    assert total == 11500


def test_should_support_multiple_users_per_receipt():
    uploader = User(name="업로더", deposit=25000)
    participant1 = User(name="참여자1", deposit=20000)
    participant2 = User(name="참여자2", deposit=15000)
    store = Store(name="카페")
    
    receipt = Receipt(user=uploader, store=store)
    receipt.add_participant(participant1)
    receipt.add_participant(participant2)
    
    assert len(receipt.participants) == 2
    assert participant1 in receipt.participants
    assert participant2 in receipt.participants
    assert receipt.uploader == uploader


def test_should_track_who_uploaded_receipt():
    uploader = User(name="김영희", deposit=30000)
    participant = User(name="박철수", deposit=20000)
    store = Store(name="맥도날드")
    
    receipt = Receipt(user=uploader, store=store)
    receipt.add_participant(participant)
    
    assert receipt.uploader == uploader
    assert receipt.uploader.name == "김영희"
    assert receipt.user == uploader  # backward compatibility
    assert receipt.uploader != participant
