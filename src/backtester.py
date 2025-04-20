
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from tools.yfinance_adapter import get_prices

class Backtester:
    def __init__(self, agent, tickers, start_date, end_date, initial_capital):
        self.agent = agent
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital

    def run(self):
        portfolio = []
        total_value = self.initial_capital
        performance = []

        for ticker in self.tickers:
            price_df = get_prices(ticker, self.start_date, self.end_date)
            if price_df is None or price_df.empty:
                raise ValueError(f"No price data for {ticker}")

            # Use adjusted close as a proxy
            price_df["Signal"] = self.agent(price_df)
            price_df["Position"] = price_df["Signal"].shift().fillna(0)
            price_df["Daily Return"] = price_df["Close"].pct_change().fillna(0)
            price_df["Strategy Return"] = price_df["Daily Return"] * price_df["Position"]
            price_df["Portfolio Value"] = (1 + price_df["Strategy Return"]).cumprod() * self.initial_capital

            portfolio.append(price_df)
            performance.append({
                "Ticker": ticker,
                "Total Return (%)": (price_df["Portfolio Value"].iloc[-1] / self.initial_capital - 1) * 100,
                "Volatility": price_df["Strategy Return"].std(),
                "Sharpe Ratio": price_df["Strategy Return"].mean() / price_df["Strategy Return"].std() * np.sqrt(252)
            })

        combined_df = portfolio[0].reset_index()
        summary_stats = pd.DataFrame(performance)

        return combined_df, summary_stats
