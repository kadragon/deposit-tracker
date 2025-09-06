from src.models.user import User


def test_user_to_dict_roundtrip():
    user = User(name="홍길동", deposit=25000)

    data = user.to_dict()

    assert data == {"name": "홍길동", "deposit": 25000}

    user2 = User.from_dict(data)
    assert user2.name == "홍길동"
    assert user2.deposit == 25000


def test_user_from_dict_defaults_missing_deposit_to_zero():
    data = {"name": "김철수"}

    user = User.from_dict(data)
    assert user.name == "김철수"
    assert user.deposit == 0

