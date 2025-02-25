from indicators import Indicators
import pandas as pd
import requests
import numpy as np
import yfinance as yf
import warnings

from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


class DataHelper:

    def __init__(self):
        self.data = None

    def load_ydata(self, ticker: str, period: str, interval: str):
        """
        :param ticker: Ticker for CIK
        :param period: The period of data to download
        :param interval: The interval of data
        :return: Loads data from Yahoo Finance
        """

        session = CachedLimiterSession(
            limiter=Limiter(RequestRate(2, Duration.SECOND * 5)),  # max 2 requests per 5 seconds
            bucket_class=MemoryQueueBucket,
            backend=SQLiteCache("yfinance.cache"),
        )

        yf_ticker = yf.Ticker(ticker, session=session)
        df_hist = yf_ticker.history(period=period, interval=interval)
        df_hist.columns = df_hist.columns.str.lower()

        self.data = df_hist

        if self.data.empty:
            print(f"Data from Yahoo Finance could not be downloaded for {ticker}.")
        else:
            print(f"Data from Yahoo Finance downloaded for {ticker}.")

    def load_data(self, df_hist: pd.DataFrame):
        """
        Loads data
        :param df_hist: Input the dataframe with Datetime Index and OHLC format
        """
        df_hist.columns = df_hist.columns.str.lower()
        self.data = df_hist

        print(f"Success: data loaded.")

    def get_cik(self, ticker: str):
        """
        :param ticker: The ticker of interest
        :return str: The CIK code of each ticker
        """
        url = "https://www.sec.gov/files/company_tickers_exchange.json"

        headers = {"User-Agent": "YourName (your@email.com)", "Accept-Encoding": "gzip, deflate"}

        response = requests.get(url, headers=headers)

        response = response.json()["data"]
        dict_data = {i[2]: str(i[0]).zfill(10) for i in response}

        cik_code = dict_data[ticker]

        return cik_code

    def earnings_date(self, ticker: str):
        """
        :param ticker: Ticker
        :return list: Returns a list of timestamp containing the earnings dates for the chosen ticker
        """
        cik = self.get_cik(ticker)
        url = "https://data.sec.gov/submissions/CIK" + cik + ".json"

        headers = {"User-Agent": "YourName (your@email.com)", "Accept-Encoding": "gzip, deflate", "Host": "data.sec.gov"}

        response = requests.get(url, headers=headers)

        json_data = response.json()  # Parse JSON response
        form_types = json_data["filings"]["recent"]["form"]
        dates = json_data["filings"]["recent"]["filingDate"]

        df_dates = pd.DataFrame({"Date": dates, "Form_Type": form_types})
        df_dates = df_dates[df_dates["Form_Type"].isin(["10-Q", "10-K"])]
        df_dates["Date"] = pd.to_datetime(df_dates["Date"])
        return list(df_dates["Date"])

    def next_earnings_date(self, date, earnings_dates):
        """
        :param date: A given date
        :param earnings_dates: Earnings dates list
        :return: Returns the next date for date in the list of earnings_dates
        """
        if date.tzinfo is not None:
            date = date.tz_convert(None)
            date = date.replace(tzinfo=None)

        earnings_dates = np.sort(np.array(earnings_dates, dtype='datetime64[D]'))
        date = np.datetime64(date, 'D')
        index = np.searchsorted(earnings_dates, date)
        if index < len(earnings_dates):
            return earnings_dates[index]
        else:
            return earnings_dates[-1] + np.timedelta64(90, 'D')

    def add_next_earnings(self, ticker: str):
        """
        :param ticker: Ticker
        :return: Adds the column to the data that contains the number of days to next earnings report
        """
        earnings_dates = self.earnings_date(ticker)

        self.data["next_earnings"] = self.data.index.map(lambda x: self.next_earnings_date(x, earnings_dates))

        self.data["next_earnings"] = self.data["next_earnings"].dt.tz_localize(None)
        self.data.index = self.data.index.tz_localize(None)

        self.data["days_to_earnings"] = (self.data["next_earnings"] - self.data.index).dt.days

    def add_indicator(self, indicator_name: str, indicator_method: str, *args):
        """
        :param indicator_name: The name of the column to be added
        :param indicator_method: The indicator method to add
        :return: Adds the indicator to the data
        """
        indi_methods = [method for method in dir(Indicators) if not method.startswith("__")]
        indi_methods.append("days_to_earnings")

        if self.data is None:
            print("There is no data loaded, please call the 'load_data' method.")

        else:
            if indicator_method in indi_methods:
                self.data[indicator_name] = getattr(Indicators(self.data), indicator_method)(*args)
                print(f"The indicator '{indicator_name}' has been added.")

            else:
                warnings.warn(f"The indicator method '{indicator_method}' you have chosen is not in the Indicators class, please pass one of the following: {indi_methods}.", UserWarning, stacklevel=1)
