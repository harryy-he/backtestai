# Class for indicators


class Indicators:

    def __init__(self, hist_df):
        """
        Assumes hist_df has an open, high, low, close and volume columns, and date index column
        """
        self.hist_df = hist_df

    def sma(self, n_days):
        """
        Returns simple moving average of close prices
        """

        hist_sma = self.hist_df["close"].rolling(n_days).mean()

        return hist_sma

    def ema(self, n_days):
        """
        Returns the Exponential Moving Average (EMA) of close prices
        """
        hist_ema = self.hist_df["close"].ewm(span=n_days, adjust=False).mean()

        return hist_ema

    def rsi(self, n_days):
        """
        Returns the RSI using exponential moving average - standard
        """
        diff = self.hist_df.diff(1)["close"]

        diff_up = diff.where(diff > 0, 0)
        diff_dwn = -diff.where(diff < 0, 0)

        ema_up = diff_up.ewm(alpha=1 / n_days, min_periods=n_days).mean()
        ema_dwn = diff_dwn.ewm(alpha=1 / n_days, min_periods=n_days).mean()

        rs = ema_up / ema_dwn

        rsi = 100 - (100 / (1 + rs))

        return rsi

    def bollinger_band_lower(self, n_days=20):
        """
        Returns the lower Bollinger Bands of close prices
        """

        multiplier = 2

        mid_band = self.hist_df["close"].rolling(n_days).mean()
        std_dev = self.hist_df["close"].rolling(n_days).std()

        lower_band = mid_band - (multiplier * std_dev)

        return lower_band

    def bollinger_band_upper(self, n_days=20):
        """
        Returns the upper Bollinger Bands of close prices
        """

        multiplier = 2

        mid_band = self.hist_df["close"].rolling(n_days).mean()
        std_dev = self.hist_df["close"].rolling(n_days).std()

        upper_band = mid_band + (multiplier * std_dev)

        return upper_band
