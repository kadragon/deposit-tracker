import pytest
from src.models.user import User
from src.models.store import Store
from src.models.receipt import Receipt
from src.services.transaction_service import TransactionService


def test_should_process_transaction_with_deposit():
    user = User(name="홍길동", deposit=10000)
    store = Store(name="이마트")
    receipt = Receipt(user=user, store=store)
    receipt.add_item("사과", 2000, 2)  # 4000원
    
    transaction_service = TransactionService()
    result = transaction_service.process_transaction(receipt, use_deposit=True)
    
    assert result.success is True
    assert result.amount_paid == 4000
    assert result.deposit_used == 4000
    assert result.cash_paid == 0
    assert user.deposit == 6000  # 10000 - 4000


def test_should_process_transaction_without_deposit():
    user = User(name="홍길동", deposit=10000)
    store = Store(name="이마트")
    receipt = Receipt(user=user, store=store)
    receipt.add_item("사과", 2000, 2)  # 4000원
    
    transaction_service = TransactionService()
    result = transaction_service.process_transaction(receipt, use_deposit=False)
    
    assert result.success is True
    assert result.amount_paid == 4000
    assert result.deposit_used == 0
    assert result.cash_paid == 4000
    assert user.deposit == 10000  # unchanged


def test_should_reject_transaction_if_insufficient_deposit():
    user = User(name="홍길동", deposit=3000)  # 부족한 예치금
    store = Store(name="이마트")
    receipt = Receipt(user=user, store=store)
    receipt.add_item("사과", 2000, 3)  # 6000원 (3000원보다 많음)
    
    transaction_service = TransactionService()
    result = transaction_service.process_transaction(receipt, use_deposit=True)
    
    assert result.success is False
    assert result.amount_paid == 0
    assert result.deposit_used == 0
    assert result.cash_paid == 0
    assert user.deposit == 3000  # unchanged


def test_should_process_split_payment_for_multiple_users():
    # Create users with different deposit amounts
    user1 = User(name="김철수", deposit=15000)
    user2 = User(name="박영희", deposit=12000)  
    user3 = User(name="이민수", deposit=8000)
    
    # Create receipt with split items
    store = Store(name="카페")
    receipt = Receipt(user=user1, store=store)  # user1 uploaded
    receipt.add_participant(user2)
    receipt.add_participant(user3)
    
    receipt.add_item("커피", 4500, 1)     # user1
    receipt.add_item("케이크", 6000, 1)   # user2
    receipt.add_item("피자", 18000, 1)    # shared by all 3
    
    receipt.items[0].assign_to_user(user1)
    receipt.items[1].assign_to_user(user2)
    receipt.items[2].assign_to_user(user1)
    receipt.items[2].assign_to_user(user2)
    receipt.items[2].assign_to_user(user3)
    
    # Process split payment
    transaction_service = TransactionService()
    results = transaction_service.handle_partial_payment_failures(receipt, use_deposit=True)
    
    # Verify split payment results
    assert len(results) == 3
    assert all(result.success for result in results.values())
    
    # Check individual amounts: user1=10500, user2=12000, user3=6000
    assert results[user1].amount_paid == 10500  # 4500 + 6000
    assert results[user2].amount_paid == 12000  # 6000 + 6000  
    assert results[user3].amount_paid == 6000   # 6000
    
    # Check deposit deductions
    assert user1.deposit == 4500   # 15000 - 10500
    assert user2.deposit == 0      # 12000 - 12000
    assert user3.deposit == 2000   # 8000 - 6000


def test_should_handle_partial_payment_failures():
    # Create users - one with insufficient deposit
    user1 = User(name="김철수", deposit=15000)  # sufficient for his 8000 share
    user2 = User(name="박영희", deposit=5000)   # insufficient for his 15500 share
    user3 = User(name="이민수", deposit=20000)  # sufficient for his 15500 share
    
    # Create receipt with split items
    store = Store(name="레스토랑")
    receipt = Receipt(user=user1, store=store)
    receipt.add_participant(user2)
    receipt.add_participant(user3)
    
    receipt.add_item("메인요리", 24000, 1)    # shared by all 3 = 8000 each
    receipt.add_item("디저트", 15000, 1)     # shared by user2, user3 = 7500 each
    
    receipt.items[0].assign_to_user(user1)  # 메인요리 shared by all
    receipt.items[0].assign_to_user(user2)  
    receipt.items[0].assign_to_user(user3)
    
    receipt.items[1].assign_to_user(user2)  # 디저트 shared by user2, user3
    receipt.items[1].assign_to_user(user3)
    
    # Process split payment - user2 needs 15500 but has only 5000
    transaction_service = TransactionService()
    results = transaction_service.handle_partial_payment_failures(receipt, use_deposit=True)
    
    # Verify partial failure handling
    assert len(results) == 3
    assert results[user1].success == True   # 8000 <= 15000
    assert results[user2].success == False  # 15500 > 5000  
    assert results[user3].success == True   # 15500 <= 20000
    
    # Check that only successful payments were processed
    assert results[user1].amount_paid == 8000
    assert results[user2].amount_paid == 0      # failed
    assert results[user3].amount_paid == 15500
    
    # Check deposit changes only for successful payments
    assert user1.deposit == 7000   # 15000 - 8000
    assert user2.deposit == 5000   # unchanged (failed)
    assert user3.deposit == 4500   # 20000 - 15500


def test_should_rollback_on_insufficient_funds():
    # Create users - one with insufficient deposit
    user1 = User(name="김철수", deposit=15000)  # sufficient 
    user2 = User(name="박영희", deposit=5000)   # insufficient
    user3 = User(name="이민수", deposit=20000)  # sufficient
    
    # Store original deposit amounts for rollback verification
    original_deposits = {
        user1: user1.deposit,
        user2: user2.deposit,
        user3: user3.deposit
    }
    
    # Create receipt with split items
    store = Store(name="레스토랑")
    receipt = Receipt(user=user1, store=store)
    receipt.add_participant(user2)
    receipt.add_participant(user3)
    
    receipt.add_item("메인요리", 24000, 1)    # shared by all 3 = 8000 each
    receipt.add_item("디저트", 15000, 1)     # shared by user2, user3 = 7500 each
    
    receipt.items[0].assign_to_user(user1)
    receipt.items[0].assign_to_user(user2)  
    receipt.items[0].assign_to_user(user3)
    
    receipt.items[1].assign_to_user(user2)
    receipt.items[1].assign_to_user(user3)
    
    # Process with rollback on any insufficient funds
    transaction_service = TransactionService()
    results = transaction_service.rollback_on_insufficient_funds(receipt, use_deposit=True)
    
    # Verify all payments failed due to user2's insufficient funds
    assert len(results) == 3
    assert all(not result.success for result in results.values())
    assert all(result.amount_paid == 0 for result in results.values())
    
    # Verify all deposits were rolled back to original amounts
    assert user1.deposit == original_deposits[user1]  # 15000 (unchanged)
    assert user2.deposit == original_deposits[user2]  # 5000 (unchanged)
    assert user3.deposit == original_deposits[user3]  # 20000 (unchanged)