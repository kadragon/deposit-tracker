import pytest
from src.models.receipt_item import ReceiptItem
from src.models.user import User


def test_should_create_receipt_item_with_name_and_price():
    item = ReceiptItem(name="사과", price=2000)
    
    assert item.name == "사과"
    assert item.price == 2000


def test_should_set_default_quantity_to_one():
    item = ReceiptItem(name="사과", price=2000)
    
    assert item.quantity == 1


def test_should_calculate_item_total():
    item = ReceiptItem(name="사과", price=2000)
    item.quantity = 3
    
    total = item.calculate_total()
    
    assert total == 6000


def test_should_assign_item_to_specific_user():
    user1 = User(name="김철수", deposit=10000)
    user2 = User(name="박영희", deposit=15000)
    item = ReceiptItem(name="아메리카노", price=4500)
    
    item.assign_to_user(user1)
    
    assert len(item.assigned_users) == 1
    assert user1 in item.assigned_users
    assert user2 not in item.assigned_users


def test_should_support_item_sharing_between_users():
    user1 = User(name="김철수", deposit=10000)
    user2 = User(name="박영희", deposit=15000)
    user3 = User(name="이민수", deposit=20000)
    item = ReceiptItem(name="피자", price=24000)
    
    item.assign_to_user(user1)
    item.assign_to_user(user2)
    item.assign_to_user(user3)
    
    assert len(item.assigned_users) == 3
    assert user1 in item.assigned_users
    assert user2 in item.assigned_users
    assert user3 in item.assigned_users
    assert item.is_shared() == True


def test_should_calculate_per_user_amount_for_shared_items():
    user1 = User(name="김철수", deposit=10000)
    user2 = User(name="박영희", deposit=15000)
    user3 = User(name="이민수", deposit=20000)
    item = ReceiptItem(name="피자", price=24000)
    
    item.assign_to_user(user1)
    item.assign_to_user(user2)
    item.assign_to_user(user3)
    
    user_amounts = item.calculate_per_user_amounts()
    
    assert len(user_amounts) == 3
    assert user_amounts[user1] == 8000  # 24000 / 3
    assert user_amounts[user2] == 8000
    assert user_amounts[user3] == 8000
    assert sum(user_amounts.values()) == 24000


def test_should_handle_fractional_amounts_with_remainder():
    """Test splitting amounts that don't divide evenly (e.g., 10000 / 3)."""
    user1 = User(name="김철수", deposit=10000)
    user2 = User(name="박영희", deposit=15000)
    user3 = User(name="이민수", deposit=20000)
    item = ReceiptItem(name="커피", price=10000)
    
    item.assign_to_user(user1)
    item.assign_to_user(user2)
    item.assign_to_user(user3)
    
    user_amounts = item.calculate_per_user_amounts()
    
    assert len(user_amounts) == 3
    # First user gets remainder: 3334 (3333.33... rounded down + 1 cent remainder)
    assert user_amounts[user1] == 3334
    assert user_amounts[user2] == 3333  # 10000 / 3 = 3333.33... rounded down
    assert user_amounts[user3] == 3333
    # Verify total is exact
    assert sum(user_amounts.values()) == 10000