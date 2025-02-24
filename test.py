from ai_helper import BacktestAI
from backtest import Backtest
from datahelper import DataHelper
from indicators import Indicators
from strategy import Strategy


if __name__ == '__main__':

    # ----------------------------------------------------------------------------
    # --- 1. Testing AI Helper
    print('**** 1 ****')

    gemini_api = 'AIzaSyDH_grQD_PxWbrtEHP4qWuWaEH7auCFngw'

    backtest_ai = BacktestAI(gemini_api)
    backtest_ai.create_strategy("Simple buy and hold")
    backtest_ai.run_strategy("Download Microsoft data for the past 1 year on a daily interval")
    backtest_ai.run_strategy("Download NVIDIA data for the past 1 year on a daily interval")

    # ----------------------------------------------------------------------------
    # --- 2. Testing DataHelper
    print('**** 2 ****')

    data = DataHelper()
    data.load_ydata("MSFT", "1y", "1d")
    data.add_indicator("test", 30)
    data.add_indicator("bollinger_band_upper", 30)
    data.add_indicator("bollinger_band_lower", 30)
    data.add_indicator("rsi", 30)

    data.add_next_earnings("MSFT")

    df_hist = data.data

    # ----------------------------------------------------------------------------
    # --- 3. Testing Strategy
    print('**** 3 ****')

    my_strategy = Strategy()
    my_strategy.add_buy_signal("rsi <= 40")
    my_strategy.add_sell_signal("rsi >= 70")
    my_strategy.add_sell_signal("undefined_signal >= 70")

    # ----------------------------------------------------------------------------
    # --- 4. Testing Backtest
    print('**** 4 ****')

    bt = Backtest(my_strategy).run_strategy(df_hist)

    # ----------------------------------------------------------------------------
    # --- 5. Testing Indicators
    print('**** 5 ****')

    Indicators(df_hist).sma(20)
    Indicators(df_hist).ema(20)
    Indicators(df_hist).rsi(20)
    Indicators(df_hist).bollinger_band_lower(20)
    Indicators(df_hist).bollinger_band_upper(20)
