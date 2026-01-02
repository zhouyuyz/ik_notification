def long_entry(df) -> bool:
    """Starter: RSI<=30 and Close<VWAP."""
    rsi = df["rsi14"].iloc[-1]
    close = df["close"].iloc[-1]
    vwap = df["vwap"].iloc[-1]
    return (rsi is not None) and (rsi <= 30) and (close < vwap)

def short_entry(df) -> bool:
    """Starter: RSI>=70 and Close>VWAP."""
    rsi = df["rsi14"].iloc[-1]
    close = df["close"].iloc[-1]
    vwap = df["vwap"].iloc[-1]
    return (rsi is not None) and (rsi >= 70) and (close > vwap)
