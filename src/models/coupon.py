class Coupon:
    def __init__(self, user_id: str, store_id: str, count: int,
                 id: str | None = None):
        if int(count) < 0:
            raise ValueError("Coupon count must be non-negative")
        self.user_id = user_id
        self.store_id = store_id
        self.count = int(count)
        self.id = id

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
    def from_dict(cls, data: dict, document_id: str | None = None):
        # Defensive: clamp negative values to 0 on read
        raw_count = int(data.get("count", 0))
        safe_count = raw_count if raw_count >= 0 else 0
        return cls(
            user_id=data.get("user_id", ""),
            store_id=data.get("store_id", ""),
            count=safe_count,
            id=document_id,
        )
