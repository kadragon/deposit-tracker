import pytest
from src.models.coupon import Coupon


def test_should_create_coupon_for_user_and_store():
    coupon = Coupon(user_id="user123", store_id="store456", count=0)
    
    assert coupon.user_id == "user123"
    assert coupon.store_id == "store456"
    assert coupon.count == 0


def test_should_increment_coupon_count():
    coupon = Coupon(user_id="user123", store_id="store456", count=3)
    
    coupon.increment_count()
    
    assert coupon.count == 4


def test_should_check_if_coupon_goal_reached():
    coupon = Coupon(user_id="user123", store_id="store456", count=10)
    
    result = coupon.is_goal_reached(10)
    
    assert result is True


def test_should_check_if_coupon_goal_not_reached():
    coupon = Coupon(user_id="user123", store_id="store456", count=7)
    
    result = coupon.is_goal_reached(10)
    
    assert result is False


def test_should_reject_negative_count():
    with pytest.raises(ValueError):
        Coupon(user_id="user123", store_id="store456", count=-1)
