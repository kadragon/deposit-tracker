class User:
    def __init__(self, name, deposit=0):
        if not name or not name.strip():
            raise ValueError("User name is required")
        if deposit < 0:
            raise ValueError("Deposit must be non-negative")
        self.name = name
        self.deposit = deposit
    
    def add_deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.deposit += amount
    
    def subtract_deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount to subtract must be positive")
        if self.deposit < amount:
            raise ValueError("Insufficient deposit balance")
        self.deposit -= amount

    def to_dict(self):
        return {"name": self.name, "deposit": self.deposit}

    @classmethod
    def from_dict(cls, data: dict):
        name = data.get("name", "").strip()
        deposit = data.get("deposit", 0)
        return cls(name=name, deposit=deposit)
