from google import genai
from backtest import Backtest
from datahelper import DataHelper
from strategy import Strategy
from indicators import Indicators
import re
import json


class BacktestAI:

    def __init__(self, api_key):
        self.api_key = api_key
        self.client = genai.Client(api_key=self.api_key)
        self.strategy = None
        self.indicators = None
        self.data = None

    def create_strategy(self, message: str):

        indi_methods = [method for method in dir(Indicators) if not method.startswith("__")]

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=(
                f"Please process the following request for stock technical indicators that signal buy and sell signals. "
                f"Each indicator corresponds to one of these methods in my class: {indi_methods}. "
                f"Each method, takes one argument which is the number of days used for calculation. "
                f"If the number of days is not specified, use 20 days by default. "
                f"There is also 'days_to_earnings' that reflects the number of days to the next earnings date."
                f"There should be two outputs, the first is a JSON format output that details the indicators used, structured as follows:\n\n"
                f'[{{"name": name for indicator and arguments, "indicator": corresponding_method, "args": number_of_days}}]\n\n'
                f"The name of the indicator should reflect the arguments used for it, for example: rsi_20."
                f"The second output are the conditions that signal when to buy and sell with the condition "
                f"parsed and ENSURE that I can use the .eval method (it should consider the name of the indicator"
                f"and arguments as returned in the first output.  The output should be structured as follows: \n\n"
                f'[{{signal_type: buy/sell, condition: eval_compliant_string}}]'
                f"Your response should be only a single json output by aggregating the two outputs together "
                f"by calling the first output 'indicators' and the second 'signals'. Also, all names are lower case."
                f"Here is the request:\n{message}"
            )
        )

        cleaned_json = re.sub(r"```(json)?\n|\n```", "", response.text).strip()
        cleaned_json = json.loads(cleaned_json)

        indicators_json = cleaned_json['indicators']
        signals_json = cleaned_json['signals']

        strategy = Strategy()

        for signal in signals_json:
            signal_type = signal['signal_type']
            condition = signal['condition']

            if signal_type == 'buy':
                strategy.add_buy_signal(condition)
            elif signal_type == 'sell':
                strategy.add_sell_signal(condition)

        self.strategy = strategy
        self.indicators = indicators_json

    def run_strategy(self, message: str):

        if self.strategy is None:
            print("Please create a strategy to backtest.")

        else:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents="Please format the following request into input that will be fed into yfinance Python package"
                         ".history method, i.e. providing a ticker, period and interval. The output should json format of the "
                         "following form: {ticker: str, period: str, interval: str}. If no period or interval is specified, "
                         "please take the period to be 1 year and the interval to be daily:"
                         f"{message}."
            )

            cleaned_json = re.sub(r"```(json)?\n|\n```", "", response.text).strip()
            cleaned_json = json.loads(cleaned_json)

            ticker = cleaned_json["ticker"]
            period = cleaned_json["period"]
            interval = cleaned_json["interval"]

            data_class = DataHelper()
            data_class.load_ydata(ticker, period, interval)
            data_class.add_next_earnings(ticker)

            # ---

            for indicator in self.indicators:
                indicator_name = indicator['name']
                method_name = indicator['indicator']
                method_args = indicator['args']

                data_class.add_indicator(indicator_name, method_name, method_args)

            # ---

            self.data = data_class.data

            bt_ai = Backtest(self.strategy)
            result = bt_ai.run_strategy(data_class.data)

            return result
