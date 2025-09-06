class Store:
    def __init__(self, name):
        self.name = name
        self.coupon_enabled = False
        self.coupon_goal = 0
    
    def enable_coupon_system(self):
        self.coupon_enabled = True
    
    def set_coupon_goal(self, goal):
        if goal <= 0:
            raise ValueError("Coupon goal must be positive")
        self.coupon_goal = goal

    def to_dict(self):
        return {
            "name": self.name,
            "coupon_enabled": self.coupon_enabled,
            "coupon_goal": self.coupon_goal,
        }

    @classmethod
    def from_dict(cls, data: dict):
        store = cls(name=data.get("name", ""))
        store.coupon_enabled = bool(data.get("coupon_enabled", False))
        store.coupon_goal = int(data.get("coupon_goal", 0))
        return store
