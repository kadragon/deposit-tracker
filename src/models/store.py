class Store:
    def __init__(self, name):
        self.name = name
        self.coupon_enabled = False
        self.coupon_goal = 0
    
    def enable_coupon_system(self):
        self.coupon_enabled = True
    
    def set_coupon_goal(self, goal):
        self.coupon_goal = goal