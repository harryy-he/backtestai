from google import genai
from backtest import Backtest
from datahelper import DataHelper
from indicators import Indicators
import re
import json

class BacktestAI():

    def __init__(self, api_key):
        self.api_key = api_key
        self.client = genai.Client(api_key=self.api_key)
        self.data = None

    def load_data(self, message: str):

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

        data = DataHelper()
        data.load_ydata(ticker, period, interval)
        data.add_next_earnings(ticker)

        self.data = data

        return self.data.data

    def load_indicators(self, message: str):

        indi_methods = [method for method in dir(Indicators) if not method.startswith("__")]

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=(
                f"Please process the following request for stock technical indicators. "
                f"Each indicator corresponds to one of these methods in my class: {indi_methods}. "
                f"Each method takes one argument, which is the number of days used for calculation. "
                f"If the number of days is not specified, use 20 days by default. "
                f"Return the output in JSON format, structured as follows:\n\n"
                f'[{{"indicator": "corresponding_method", "args": number_of_days}}]\n\n'
                f"Here is the request:\n{message}"
            )
        )

        cleaned_json = re.sub(r"```(json)?\n|\n```", "", response.text).strip()
        cleaned_json = json.loads(cleaned_json)

        for response in cleaned_json:
            method_name = response['indicator']
            method_args = response['args']

            self.data.add_indicator(method_name, method_args)

        return self.data.data



if __name__ == '__main__':

    gemini_api = 'AIzaSyDH_grQD_PxWbrtEHP4qWuWaEH7auCFngw'

    bt_ai = BacktestAI(gemini_api)

    bt_ai.load_data("Download Qualcomm data for the past 3 years on a daily interval")
    bt_ai.load_indicators("Add the rsi of 50 days")