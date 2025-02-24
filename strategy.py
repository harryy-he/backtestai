# Class for defining strategies

class Strategy:
    def __init__(self):
        self.buys = []
        self.sells = []

    def add_buy_signal(self, condition: str):
        self.buys.append(condition)
        print(f"Adding buy condition {condition}")

    def add_sell_signal(self, condition: str):
        self.sells.append(condition)
        print(f"Adding sell condition {condition}")

    def remove_buy_signal(self, condition: str):
        self.buys.remove(condition)
        print(f"Removing buy condition {condition}")

    def remove_sell_signal(self, condition: str):
        self.sells.remove(condition)
        print(f"Removing sell condition {condition}")
