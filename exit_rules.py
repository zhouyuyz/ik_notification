from __future__ import annotations
from typing import Tuple, Optional

def should_exit_long(
    close: float,
    vwap: float,
    rsi14: float,
    avg_price: float,
    take_profit_pct: float,
    stop_loss_pct: float,
    exit_rsi_long: float,
) -> Tuple[bool, Optional[str]]:
    if avg_price <= 0:
        return False, None

    if close >= avg_price * (1 + take_profit_pct):
        return True, f"TP hit: close {close:.2f} >= {avg_price*(1+take_profit_pct):.2f}"
    if close <= avg_price * (1 - stop_loss_pct):
        return True, f"SL hit: close {close:.2f} <= {avg_price*(1-stop_loss_pct):.2f}"
    if (rsi14 >= exit_rsi_long) and (close > vwap):
        return True, f"Mean-revert: RSI {rsi14:.1f}>= {exit_rsi_long} & C>VWAP"
    return False, None

def should_exit_short(
    close: float,
    vwap: float,
    rsi14: float,
    avg_price: float,
    take_profit_pct: float,
    stop_loss_pct: float,
    exit_rsi_short: float,
) -> Tuple[bool, Optional[str]]:
    if avg_price <= 0:
        return False, None

    if close <= avg_price * (1 - take_profit_pct):
        return True, f"TP hit: close {close:.2f} <= {avg_price*(1-take_profit_pct):.2f}"
    if close >= avg_price * (1 + stop_loss_pct):
        return True, f"SL hit: close {close:.2f} >= {avg_price*(1+stop_loss_pct):.2f}"
    if (rsi14 <= exit_rsi_short) and (close < vwap):
        return True, f"Mean-revert: RSI {rsi14:.1f}<= {exit_rsi_short} & C<VWAP"
    return False, None
