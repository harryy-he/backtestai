# Class for indicators

import pandas as pd

class Backtest():

    def __init__(self):
        self.buys = []
        self.sells = []
        self.data = None

    def add_buy_signal(self, condition: str):
        self.buys.append(condition)

    def add_sell_signal(self, condition: str):
        self.sells.append(condition)

    def generate_data(self, df: pd.DataFrame):
        self.data = df.copy()
        self.data = self.data.dropna()
        self.data = self.data.reset_index(drop=True)

        # ---

        added_buys = []
        added_sells = []

        for condition in self.buys:
            try:
                self.data[condition] = self.data.eval(condition)
                print(f"Adding buy condition {condition}")
                added_buys.append(condition)
            except:
                print(f"Please check condition '{condition}' - looks like a column is missing.")

        for condition in self.sells:
            try:
                self.data[condition] = self.data.eval(condition)
                added_sells.append(condition)
                print(f"Adding sell condition {condition}")
            except:
                print(f"Please check condition '{condition}' - looks like a column is missing.")

        # ---

        if len(added_buys) == 0:
            self.data["buy_signal"] = 0
        else:
            self.data["buy_signal"] = 1
            for condition in added_buys:
                self.data["buy_signal"] *= self.data[condition]

        # ---

        if len(added_sells) == 0:
            self.data["sell_signal"] = 0
        else:
            self.data["sell_signal"] = 1
            for condition in added_sells:
                self.data["sell_signal"] *= self.data[condition]

        # ---

        self.data["holding_signal"] = 0
        if self.data["buy_signal"].iloc[0] == 1:
            self.data.loc[0, "holding_signal"] = 1

        for i in range(1, len(self.data)):
            if self.data["buy_signal"].iloc[i] == 1 and self.data["sell_signal"].iloc[i] == 1:
                self.data.loc[i, "holding_signal"] = self.data.loc[i - 1, "holding_signal"]
            elif self.data["buy_signal"].iloc[i] == 0 and self.data["sell_signal"].iloc[i] == 0:
                self.data.loc[i, "holding_signal"] = self.data.loc[i - 1, "holding_signal"]
            elif self.data["buy_signal"].iloc[i] == 1:
                self.data.loc[i, "holding_signal"] = 1
            elif self.data["sell_signal"].iloc[i] == 1:
                self.data.loc[i, "holding_signal"] = 0

        self.data = self.data.dropna()

    def run_strategy(self):

        if self.data is None:
            print("Please call 'load_data' method with appropriate dataframe.")

        else:
            print("Running strategy...")
            cash = 100
            start = cash

            position = 0
            val = []

            for i in range(len(self.data)):

                if self.data["holding_signal"].iloc[i] == 1 and cash > 0:
                    position = cash / self.data["close"].iloc[i]
                    cash = 0

                elif self.data["holding_signal"].iloc[i] == 0 and position > 0:
                    cash = position * self.data["close"].iloc[i]
                    position = 0

                val.append(cash + position * self.data["close"].iloc[i])

            final_val = cash + position * self.data["close"].iloc[-1]

            pct_chg = (final_val / start) - 1

            return final_val, pct_chg

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

    my_strategy = Backtest()
    my_strategy.add_buy_signal("rsi <= 40")
    my_strategy.add_sell_signal("rsi >= 70")
    my_strategy.generate_data(df)

    df_data = my_strategy.data

    bt_result = my_strategy.run_strategy()