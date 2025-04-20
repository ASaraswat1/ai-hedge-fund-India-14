
import yfinance as yf
import pandas as pd
from datetime import datetime

def get_prices(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch historical price data for the given ticker using yfinance.

    Handles both single-level and multi-index column formats.
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty:
            raise ValueError(f"No data found for ticker: {ticker}")

        # If columns are multi-index (e.g., ('Close', 'RELIANCE.NS')), flatten them
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        expected_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing = [col for col in expected_cols if col not in data.columns]
        if missing:
            raise ValueError(f"Missing columns {missing} for ticker: {ticker}. Columns available: {list(data.columns)}")

        data = data[expected_cols]
        data.index = pd.to_datetime(data.index)
        return data
    except Exception as e:
        raise RuntimeError(f"Error fetching data for {ticker}: {str(e)}")
