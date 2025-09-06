import pytest
from src.models.store import Store


@pytest.mark.parametrize("goal", [0, -1, -10])
def test_set_coupon_goal_must_be_positive(goal):
    store = Store(name="편의점A")

    with pytest.raises(ValueError, match="Coupon goal must be positive"):
        store.set_coupon_goal(goal)

