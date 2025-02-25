# Class for indicators
import warnings

import numpy as np
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

        print("Running strategy...")

        data = self.generate_signals(df)
        cash = 100  # Initial capital
        start = cash
        position = 0
        val = []
        winrate = []
        opening_trade_price = None

        for i in range(len(data)):
            close_price = data["close"].iloc[i]

            # Opening position
            if data["holding_signal"].iloc[i] == 1 and cash > 0:
                position = cash / close_price
                cash = 0
                opening_trade_price = close_price

            # Closing position
            elif data["holding_signal"].iloc[i] == 0 and position > 0:
                cash = position * close_price
                position = 0
                closing_trade_price = close_price

                trade_pct = (closing_trade_price/opening_trade_price) - 1
                winrate.append(trade_pct)

            # --- Getting value of portfolio

            current_val = cash + (position * data["close"].iloc[i])
            val.append(current_val)

        if position > 0:  # Selling at end
            close_price = data["close"].iloc[-1]
            cash = position * close_price
            closing_trade_price = close_price

            trade_pct = (closing_trade_price / opening_trade_price) - 1
            winrate.append(trade_pct)

        # ---- Metrics

        final_val = cash
        pct_chg = (final_val / start) - 1

        # Winrate
        if len(winrate) > 0:
            win_rate = sum(x > 0 for x in winrate)/len(winrate)
        else:
            win_rate = 0

        num_trades = len(winrate)

        print(f"Final Value: {final_val:.2f}")
        print(f"Total Return: {pct_chg * 100:.2f}%")
        print(f"Win Rate: {win_rate * 100:.2f}%")
        print(f"Total Trades: {num_trades}")

        return final_val, pct_chg, num_trades, win_rate, data
