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