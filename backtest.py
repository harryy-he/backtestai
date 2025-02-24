# Class for indicators

import pandas as pd
from strategy import Strategy

class Backtest():

    def __init__(self, strategy: Strategy):
        self.strategy = strategy

    def generate_signals(self, df: pd.DataFrame):

        data = df.copy()
        data = data.dropna()
        data = data.reset_index(drop=True)

        # ---

        added_buys = []
        added_sells = []

        for condition in self.strategy.buys:
            try:
                data[condition] = data.eval(condition)
                added_buys.append(condition)
            except:
                print(
                    f"Please check condition '{condition}' - looks like a column is missing.")

        for condition in self.strategy.sells:
            try:
                data[condition] = data.eval(condition)
                added_sells.append(condition)
            except:
                print(
                    f"Please check condition '{condition}' - looks like a column is missing.")

        # ---

        if len(added_buys) == 0:
            data["buy_signal"] = 0
        else:
            data["buy_signal"] = 1
            for condition in added_buys:
                data["buy_signal"] *= data[condition]

        # ---

        if len(added_sells) == 0:
            data["sell_signal"] = 0
        else:
            data["sell_signal"] = 1
            for condition in added_sells:
                data["sell_signal"] *= data[condition]

        # ---

        data["holding_signal"] = 0
        if data["buy_signal"].iloc[0] == 1:
            data.loc[0, "holding_signal"] = 1

        for i in range(1, len(data)):
            if data["buy_signal"].iloc[i] == 1 and data["sell_signal"].iloc[i] == 1:
                data.loc[i, "holding_signal"] = data.loc[i - 1, "holding_signal"]
            elif data["buy_signal"].iloc[i] == 0 and data["sell_signal"].iloc[i] == 0:
                data.loc[i, "holding_signal"] = data.loc[i - 1, "holding_signal"]
            elif data["buy_signal"].iloc[i] == 1:
                data.loc[i, "holding_signal"] = 1
            elif data["sell_signal"].iloc[i] == 1:
                data.loc[i, "holding_signal"] = 0

        return data

    def run_strategy(self, df: pd.DataFrame):

        data = self.generate_signals(df)

        print("Running strategy...")

        # ---

        cash = 100
        start = cash

        position = 0
        val = []

        for i in range(len(data)):

            if data["holding_signal"].iloc[i] == 1 and cash > 0:
                position = cash / data["close"].iloc[i]
                cash = 0

            elif data["holding_signal"].iloc[i] == 0 and position > 0:
                cash = position * data["close"].iloc[i]
                position = 0

            val.append(cash + position * data["close"].iloc[i])

        final_val = cash + position * data["close"].iloc[-1]

        pct_chg = (final_val / start) - 1

        # ---

        # no_trades = self.data["holdig_signal"].diff().fillna(0)

        print(final_val, pct_chg)

        return final_val, pct_chg

if __name__ == '__main__':

    from datahelper import DataHelper

    data = DataHelper()
    data.load_ydata("MSFT", "1y", "1d")
    data.add_indicator("bollinger_band_upper", 30)
    data.add_indicator("bollinger_band_lower", 30)
    data.add_indicator("rsi", 20)

    data.add_next_earnings("MSFT")

    df = data.data

    # ---

    my_strategy = Strategy()
    my_strategy.add_buy_signal("rsi <= 40")
    my_strategy.add_sell_signal("rsi >= 70")

    # ---

    bt = Backtest(my_strategy).run_strategy(df)

