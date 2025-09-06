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