class ReceiptItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.quantity = 1
    
    def calculate_total(self):
        return self.price * self.quantity