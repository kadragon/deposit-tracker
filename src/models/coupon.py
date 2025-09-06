class Coupon:
    def __init__(self, user_id: str, store_id: str, count: int):
        self.user_id = user_id
        self.store_id = store_id
        self.count = count
    
    def increment_count(self):
        self.count += 1
    
    def is_goal_reached(self, goal: int) -> bool:
        return self.count >= goal
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "store_id": self.store_id,
            "count": self.count,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            user_id=data.get("user_id", ""),
            store_id=data.get("store_id", ""),
            count=int(data.get("count", 0))
        )