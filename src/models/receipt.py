class Receipt:
    def __init__(self, user, store):
        self.user = user
        self.store = store
        self.items = []
    
    def add_item(self, name, price, quantity):
        item = {
            "name": name,
            "price": price,
            "quantity": quantity
        }
        self.items.append(item)
    
    def calculate_total(self):
        total = 0
        for item in self.items:
            total += item["price"] * item["quantity"]
        return total