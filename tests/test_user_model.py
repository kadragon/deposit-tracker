import pytest
from src.models.user import User


def test_should_create_user_with_name_and_initial_deposit():
    user = User(name="홍길동", deposit=25000)
    
    assert user.name == "홍길동"
    assert user.deposit == 25000