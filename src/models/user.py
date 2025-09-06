class User:
    def __init__(self, name, deposit=0):
        if not name or not name.strip():
            raise ValueError("User name is required")
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