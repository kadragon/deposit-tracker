from src.models.store import Store


def test_store_to_dict_roundtrip():
    store = Store(name="편의점A")
    store.enable_coupon_system()
    store.set_coupon_goal(10)

    data = store.to_dict()

    assert data == {"name": "편의점A", "coupon_enabled": True, "coupon_goal": 10}

    store2 = Store.from_dict(data)
    assert store2.name == "편의점A"
    assert store2.coupon_enabled is True
    assert store2.coupon_goal == 10


def test_store_from_dict_defaults():
    data = {"name": "편의점B"}

    store = Store.from_dict(data)
    assert store.name == "편의점B"
    assert store.coupon_enabled is False
    assert store.coupon_goal == 0

