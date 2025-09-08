import pytest
from unittest.mock import Mock, call
from src.services.coupon_service import CouponService
from src.models.store import Store
from src.models.coupon import Coupon


def test_should_award_coupon_for_purchase():
    # Arrange
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    
    store = Store(name="카페 A")
    store.enable_coupon_system()
    store.set_coupon_goal(10)
    mock_store_repo.get_by_id.return_value = store
    
    # Repository handles increment internally
    
    service = CouponService(mock_coupon_repo, mock_store_repo)
    
    # Act
    service.award_coupon_for_purchase("user123", "store456")
    
    # Assert
    mock_store_repo.get_by_id.assert_called_once_with("store456")
    mock_coupon_repo.increment.assert_called_once_with("user123", "store456", 10)


def test_should_not_award_coupon_if_disabled():
    # Arrange
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    
    store = Store(name="카페 A")
    # Don't enable coupon system - coupon_enabled is False by default
    mock_store_repo.get_by_id.return_value = store
    
    service = CouponService(mock_coupon_repo, mock_store_repo)
    
    # Act
    service.award_coupon_for_purchase("user123", "store456")
    
    # Assert
    mock_store_repo.get_by_id.assert_called_once_with("store456")
    mock_coupon_repo.increment.assert_not_called()


def test_should_reset_coupon_when_goal_reached():
    # Arrange
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    
    store = Store(name="카페 A")
    store.enable_coupon_system()
    store.set_coupon_goal(10)
    mock_store_repo.get_by_id.return_value = store
    
    # Repository will handle reset when reaching goal
    
    service = CouponService(mock_coupon_repo, mock_store_repo)
    
    # Act
    service.award_coupon_for_purchase("user123", "store456")
    
    # Assert
    mock_store_repo.get_by_id.assert_called_once_with("store456")
    mock_coupon_repo.increment.assert_called_once_with("user123", "store456", 10)


def test_should_not_award_coupon_if_store_not_found():
    # Arrange
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    
    # Store not found - returns None
    mock_store_repo.get_by_id.return_value = None
    
    service = CouponService(mock_coupon_repo, mock_store_repo)
    
    # Act
    service.award_coupon_for_purchase("user123", "store456")
    
    # Assert
    mock_store_repo.get_by_id.assert_called_once_with("store456")
    mock_coupon_repo.increment.assert_not_called()


def test_should_award_coupon_only_to_actual_payers():
    # Arrange
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    
    store = Store(name="스타벅스")
    store.enable_coupon_system()
    store.set_coupon_goal(10)
    mock_store_repo.get_by_id.return_value = store
    
    service = CouponService(mock_coupon_repo, mock_store_repo)
    
    # Act - Award coupon based on split transaction data
    # Only users with non-zero amounts should get coupons
    split_transactions = {
        "user1": "5000",  # Actual payer - should get coupon
        "user2": "3000",  # Actual payer - should get coupon  
        "user3": "0"      # Zero amount - should NOT get coupon
    }
    
    service.award_coupons_for_split_payment("store456", split_transactions)
    
    # Assert - Only actual payers should get coupons
    mock_store_repo.get_by_id.assert_called_once_with("store456")
    
    # Should call increment only for users with non-zero amounts
    expected_calls = [
        call("user1", "store456", 10),
        call("user2", "store456", 10)
    ]
    mock_coupon_repo.increment.assert_has_calls(expected_calls, any_order=True)
    
    # Should not call increment for user3 (zero amount)
    assert mock_coupon_repo.increment.call_count == 2


def test_should_not_award_coupon_for_zero_amount_users():
    # Arrange
    mock_coupon_repo = Mock()
    mock_store_repo = Mock()
    
    store = Store(name="스타벅스")
    store.enable_coupon_system() 
    store.set_coupon_goal(10)
    mock_store_repo.get_by_id.return_value = store
    
    service = CouponService(mock_coupon_repo, mock_store_repo)
    
    # Act - All users have zero amount (edge case)
    split_transactions = {
        "user1": "0",
        "user2": "0", 
        "user3": "0"
    }
    
    service.award_coupons_for_split_payment("store456", split_transactions)
    
    # Assert - No coupons should be awarded
    mock_store_repo.get_by_id.assert_called_once_with("store456")
    mock_coupon_repo.increment.assert_not_called()
