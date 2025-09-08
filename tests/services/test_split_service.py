import pytest
from src.models.user import User
from src.models.store import Store
from src.models.receipt import Receipt
from src.services.split_service import SplitService


def test_should_split_receipt_items_by_user_assignment():
    # Create users
    user1 = User(name="김철수", deposit=20000)
    user2 = User(name="박영희", deposit=15000)
    user3 = User(name="이민수", deposit=25000)
    
    # Create receipt with items
    store = Store(name="카페")
    receipt = Receipt(user=user1, store=store)
    receipt.add_participant(user2)
    receipt.add_participant(user3)
    
    # Add items and assign to users
    receipt.add_item("아메리카노", 4500, 1)  # user1만
    receipt.add_item("라떼", 5000, 1)       # user2만
    receipt.add_item("피자", 18000, 1)      # user1, user2, user3 공유
    
    receipt.items[0].assign_to_user(user1)           # 아메리카노 -> user1
    receipt.items[1].assign_to_user(user2)           # 라떼 -> user2
    receipt.items[2].assign_to_user(user1)           # 피자 -> 공유
    receipt.items[2].assign_to_user(user2)
    receipt.items[2].assign_to_user(user3)
    
    # Split the receipt
    split_service = SplitService()
    user_amounts = split_service.split_receipt_by_user_assignment(receipt)
    
    # Verify split amounts
    assert len(user_amounts) == 3
    assert user_amounts[user1] == 10500  # 4500 + (18000/3)
    assert user_amounts[user2] == 11000  # 5000 + (18000/3)  
    assert user_amounts[user3] == 6000   # (18000/3)
    assert sum(user_amounts.values()) == 27500  # Total receipt amount


def test_should_calculate_individual_amounts():
    # Create users
    user1 = User(name="김철수", deposit=20000)
    user2 = User(name="박영희", deposit=15000)
    
    # Create receipt with individual items only
    store = Store(name="편의점")
    receipt = Receipt(user=user1, store=store)
    receipt.add_participant(user2)
    
    # Add individual items (no sharing)
    receipt.add_item("물", 1000, 1)        # user1
    receipt.add_item("커피", 2500, 2)      # user2 (quantity 2)
    receipt.add_item("과자", 1800, 1)      # user1
    
    receipt.items[0].assign_to_user(user1)  # 물 -> user1
    receipt.items[1].assign_to_user(user2)  # 커피 -> user2
    receipt.items[2].assign_to_user(user1)  # 과자 -> user1
    
    # Calculate individual amounts
    split_service = SplitService()
    individual_amounts = split_service.calculate_individual_amounts(receipt)
    
    # Verify individual amounts (no sharing)
    assert len(individual_amounts) == 2
    assert individual_amounts[user1] == 2800  # 1000 + 1800
    assert individual_amounts[user2] == 5000  # 2500 * 2
    assert sum(individual_amounts.values()) == 7800  # Total receipt amount


def test_should_validate_all_items_are_assigned():
    # Create users
    user1 = User(name="김철수", deposit=20000)
    user2 = User(name="박영희", deposit=15000)
    
    # Create receipt with some unassigned items
    store = Store(name="카페")
    receipt = Receipt(user=user1, store=store)
    receipt.add_participant(user2)
    
    # Add items - some assigned, some not
    receipt.add_item("커피", 4500, 1)      # assigned
    receipt.add_item("케이크", 6000, 1)    # not assigned
    receipt.add_item("음료", 3000, 1)      # assigned
    
    receipt.items[0].assign_to_user(user1)  # 커피 -> assigned
    # items[1] is not assigned (케이크)
    receipt.items[2].assign_to_user(user2)  # 음료 -> assigned
    
    # Test validation
    split_service = SplitService()
    
    # Should return False because one item is unassigned
    assert split_service.validate_all_items_assigned(receipt) == False
    
    # Assign the remaining item
    receipt.items[1].assign_to_user(user1)
    
    # Now should return True
    assert split_service.validate_all_items_assigned(receipt) == True


def test_should_handle_shared_items_proportionally():
    # Create users
    user1 = User(name="김철수", deposit=20000)
    user2 = User(name="박영희", deposit=15000)
    user3 = User(name="이민수", deposit=25000)
    
    # Create receipt with shared items only
    store = Store(name="레스토랑")
    receipt = Receipt(user=user1, store=store)
    receipt.add_participant(user2)
    receipt.add_participant(user3)
    
    # Add shared items
    receipt.add_item("샐러드", 15000, 1)    # shared by all 3
    receipt.add_item("스테이크", 24000, 1)  # shared by user1, user2
    
    # Assign items to users for sharing
    receipt.items[0].assign_to_user(user1)  # 샐러드 -> shared by all
    receipt.items[0].assign_to_user(user2)
    receipt.items[0].assign_to_user(user3)
    
    receipt.items[1].assign_to_user(user1)  # 스테이크 -> shared by 2
    receipt.items[1].assign_to_user(user2)
    
    # Calculate shared amounts
    split_service = SplitService()
    shared_amounts = split_service.handle_shared_items_proportionally(receipt)
    
    # Verify proportional sharing
    assert len(shared_amounts) == 3
    assert shared_amounts[user1] == 17000  # (15000/3) + (24000/2) = 5000 + 12000
    assert shared_amounts[user2] == 17000  # (15000/3) + (24000/2) = 5000 + 12000
    assert shared_amounts[user3] == 5000   # (15000/3) = 5000
    assert sum(shared_amounts.values()) == 39000  # Total receipt amount