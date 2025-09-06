import pytest
from src.models.receipt_item import ReceiptItem


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