class Store:
    def __init__(self, name: str):
        self.name: str = name
        self.coupon_enabled: bool = False
        self.coupon_goal: int = 0

    def enable_coupon_system(self) -> None:
        self.coupon_enabled = True

    def set_coupon_goal(self, goal: int) -> None:
        if goal <= 0:
            raise ValueError("Coupon goal must be positive")
        self.coupon_goal = goal

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "coupon_enabled": self.coupon_enabled,
            "coupon_goal": self.coupon_goal,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Store":
        store = cls(name=data.get("name", ""))
        store.coupon_enabled = bool(data.get("coupon_enabled", False))
        store.coupon_goal = int(data.get("coupon_goal", 0))
        return store
