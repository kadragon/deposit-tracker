import pytest
from src.models.user import User


def test_user_initial_deposit_must_be_non_negative():
    with pytest.raises(ValueError, match="Deposit must be non-negative"):
        User(name="홍길동", deposit=-1)


@pytest.mark.parametrize("amount", [0, -1, -100])
def test_add_deposit_requires_positive_amount(amount):
    user = User(name="홍길동", deposit=0)

    with pytest.raises(ValueError, match="Deposit amount must be positive"):
        user.add_deposit(amount)


@pytest.mark.parametrize("amount", [0, -1, -100])
def test_subtract_deposit_requires_positive_amount(amount):
    user = User(name="홍길동", deposit=100)

    with pytest.raises(ValueError, match="Amount to subtract must be positive"):
        user.subtract_deposit(amount)
