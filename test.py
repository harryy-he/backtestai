import unittest
from ai_helper import BacktestAI
from backtest import Backtest
from datahelper import DataHelper
from indicators import Indicators
from strategy import Strategy


class TestTradingBacktest(unittest.TestCase):
    def setUp(self):
        """Set up reusable objects before each test"""
        self.my_strategy = Strategy()

        self.data = DataHelper()
        self.data.load_ydata("MSFT", "1y", "1d")

        self.api_key = 'AIzaSyDH_grQD_PxWbrtEHP4qWuWaEH7auCFngw'
        if not self.api_key:
            self.skipTest("OPENAI_API_KEY is not set in environment variables")

    def test_ai_helper(self):
        """Test AI Helper with a simple strategy"""
        print("Testing AI Helper")
        backtest_ai = BacktestAI(api_key=self.api_key)  # Use a mock API key
        backtest_ai.create_strategy("Simple buy and hold")
        result = backtest_ai.run_strategy("Download Microsoft data for the past 1 year on a daily interval")
        self.assertIsNotNone(result, "Strategy run should return data")

    def test_data_helper(self):
        """Test loading market data and adding indicators"""
        print("Testing DataHelper")
        self.data.add_indicator("rsi_20", "rsi", 20)
        self.assertIn("rsi", self.data.data.columns, "RSI should be in the dataframe")

    def test_strategy(self):
        """Test adding buy/sell signals"""
        print("Testing Strategy")
        self.my_strategy.add_buy_signal("rsi <= 40")
        self.my_strategy.add_sell_signal("rsi >= 70")
        self.assertEqual(len(self.my_strategy.buys), 1, "Buy signal should be added")
        self.assertEqual(len(self.my_strategy.sells), 1, "Sell signal should be added")

    def test_backtest(self):
        """Test running a backtest"""
        print("Testing Backtest")
        bt = Backtest(self.my_strategy)
        results = bt.run_strategy(self.data.data)
        self.assertIsNotNone(results, "Backtest should return results")

    def test_indicators(self):
        """Test indicators calculation"""
        print("Testing Indicators")
        indicators = Indicators(self.data.data)
        self.data.data["sma_20"] = indicators.sma(20)
        self.assertIn("sma_20", self.data.data.columns, "SMA should be calculated")


if __name__ == '__main__':
    unittest.main()
