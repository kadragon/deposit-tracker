import pytest
from src.models.user import User


def test_should_create_user_with_name_and_initial_deposit():
    user = User(name="홍길동", deposit=25000)
    
    assert user.name == "홍길동"
    assert user.deposit == 25000


@pytest.mark.parametrize("invalid_name", ["", "   "])
def test_should_validate_user_name_is_required(invalid_name):
    with pytest.raises(ValueError, match="User name is required"):
        User(name=invalid_name, deposit=0)


def test_should_initialize_deposit_to_zero_by_default():
    user = User(name="홍길동")
    
    assert user.name == "홍길동"
    assert user.deposit == 0


def test_should_add_deposit_amount():
    user = User(name="홍길동", deposit=25000)
    
    user.add_deposit(10000)
    
    assert user.deposit == 35000


def test_should_subtract_deposit_amount():
    user = User(name="홍길동", deposit=25000)
    
    user.subtract_deposit(5000)
    
    assert user.deposit == 20000


def test_should_not_allow_negative_deposit():
    user = User(name="홍길동", deposit=5000)
    
    with pytest.raises(ValueError, match="Insufficient deposit balance"):
        user.subtract_deposit(10000)


def test_should_not_allow_negative_add_deposit():
    user = User(name="홍길동", deposit=5000)
    
    with pytest.raises(ValueError, match="Deposit amount must be positive"):
        user.add_deposit(-1000)


def test_should_not_allow_zero_add_deposit():
    user = User(name="홍길동", deposit=5000)
    
    with pytest.raises(ValueError, match="Deposit amount must be positive"):
        user.add_deposit(0)


def test_should_not_allow_negative_subtract_deposit():
    user = User(name="홍길동", deposit=5000)
    
    with pytest.raises(ValueError, match="Amount to subtract must be positive"):
        user.subtract_deposit(-1000)


def test_should_not_allow_zero_subtract_deposit():
    user = User(name="홍길동", deposit=5000)
    
    with pytest.raises(ValueError, match="Amount to subtract must be positive"):
        user.subtract_deposit(0)