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