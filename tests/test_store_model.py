import pytest
from src.models.store import Store


def test_should_create_store_with_name():
    store = Store(name="편의점A")
    
    assert store.name == "편의점A"
    assert store.coupon_enabled is False
    assert store.coupon_goal == 0


def test_should_enable_coupon_system_for_store():
    store = Store(name="편의점A")
    
    store.enable_coupon_system()
    
    assert store.coupon_enabled is True


def test_should_set_coupon_goal_for_store():
    store = Store(name="편의점A")
    
    store.set_coupon_goal(10)
    
    assert store.coupon_goal == 10