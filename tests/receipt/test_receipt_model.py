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
