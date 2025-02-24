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


if __name__ == '__main__':

    from datahelper import DataHelper

    data = DataHelper()
    data.load_ydata("MSFT", "1y", "1d")
    data.add_indicator("test", 30)
    data.add_indicator("bollinger_band_upper", 30)
    data.add_indicator("bollinger_band_lower", 30)

    data.add_next_earnings("MSFT")

    df = data.data

    # ---

    my_strategy = Strategy()
    my_strategy.add_buy_signal("rsi <= 40")
    my_strategy.add_sell_signal("rsi >= 70")
