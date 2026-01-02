"""Indicator helpers.

We keep the indicator set intentionally small and fast for intraday polling.

Current indicators:
- RSI14
- VWAP (session cumulative)
- EMA9
- Bollinger mid (20 SMA)
- ATR14
"""

from __future__ import annotations

import numpy as np
import pandas_ta as ta

from config import *


def add_indicators(df):
    # --- Momentum / mean-reversion ---
    df["rsi14"] = ta.rsi(df["close"], length=RSI_LENGTH, mamode=RSI_MODE)

    # --- VWAP (cumulative session) ---
    tp = (df["high"] + df["low"] + df["close"]) / 3
    vol = df["volume"].replace(0, np.nan)
    df["vwap"] = (tp * vol).cumsum() / vol.cumsum()

    # --- Trend / structure ---
    df["ema9"] = ta.ema(df["close"], length=9)
    df["bb_mid"] = ta.sma(df["close"], length=20)  # Bollinger middle band (20 SMA)

    # --- Volatility ---
    df["atr14"] = ta.atr(df["high"], df["low"], df["close"], length=14)

    return df
