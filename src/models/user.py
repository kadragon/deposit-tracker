class User:
    def __init__(self, name, deposit=0):
        if not name or not name.strip():
            raise ValueError("User name is required")
        self.name = name
        self.deposit = deposit