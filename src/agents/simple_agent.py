
def simple_moving_average_agent(df):
    """
    Generates a signal based on SMA crossover.
    Buy signal (1) when SMA20 > SMA50, else 0.
    """
    df["SMA20"] = df["Adj Close"].rolling(window=20).mean()
    df["SMA50"] = df["Adj Close"].rolling(window=50).mean()
    df["Signal"] = (df["SMA20"] > df["SMA50"]).astype(int)
    return df["Signal"]
