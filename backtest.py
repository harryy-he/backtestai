# Class for indicators
import warnings

import pandas as pd
from strategy import Strategy


class Backtest:

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
            except Exception as e:
                warnings.warn(f"An unexpected error occurred: {e}", UserWarning, stacklevel=1)

        for condition in self.strategy.sells:
            try:
                data[condition] = data.eval(condition)
                added_sells.append(condition)
            except Exception as e:
                warnings.warn(f"An unexpected error occurred: {e}", UserWarning, stacklevel=1)

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
