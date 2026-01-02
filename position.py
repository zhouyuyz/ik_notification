from __future__ import annotations
from dataclasses import dataclass
import math
from typing import List, Optional, Dict, Any

@dataclass
class PositionState:
    direction: str                 # "long" or "short"
    max_capital: float
    ladder: List[float]
    option_type: str = ""         # "CALL" for long, "PUT" for short
    strike: int = 0
    contracts: int = 0
    used_capital: float = 0.0
    entry_count: int = 0
    avg_price: float = 0.0
    size: float = 0.0              # shares
    stopped_today: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "direction": self.direction,
            "option_type": self.option_type,
            "strike": self.strike,
            "contracts": self.contracts,
            "max_capital": self.max_capital,
            "ladder": list(self.ladder),
            "used_capital": self.used_capital,
            "entry_count": self.entry_count,
            "avg_price": self.avg_price,
            "size": self.size,
            "stopped_today": self.stopped_today,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "PositionState":
        return PositionState(
            direction=d.get("direction", "long"),
            option_type=str(d.get("option_type", "")),
            strike=int(d.get("strike", 0)),
            contracts=int(d.get("contracts", 0)),
            max_capital=float(d.get("max_capital", 0.0)),
            ladder=list(d.get("ladder", [])),
            used_capital=float(d.get("used_capital", 0.0)),
            entry_count=int(d.get("entry_count", 0)),
            avg_price=float(d.get("avg_price", 0.0)),
            size=float(d.get("size", 0.0)),
            stopped_today=bool(d.get("stopped_today", False)),
        )

def try_open(signal_ok: bool, price: float, state: PositionState) -> Optional[dict]:
    if not signal_ok or state.stopped_today:
        return None
    if state.entry_count >= len(state.ladder):
        return None

    pct = state.ladder[state.entry_count]
    capital = state.max_capital * pct
    if capital <= 0:
        return None

    qty = capital / price  # underlying-share proxy

    # Option proxy (for notification only):
    # LONG => CALL strike <= underlying (floor)
    # SHORT => PUT  strike >= underlying (ceil)
    if state.direction == "long":
        state.option_type = "CALL"
        state.strike = int(math.floor(price))
    else:
        state.option_type = "PUT"
        state.strike = int(math.ceil(price))

    # contracts is an approximation: capital / (underlying*100)
    state.contracts = max(1, int(round(capital / (price * 100))))

    if state.size > 0:
        state.avg_price = (state.avg_price * state.size + price * qty) / (state.size + qty)
    else:
        state.avg_price = price

    state.size += qty
    state.used_capital += capital
    state.entry_count += 1

    return {
        "direction": state.direction,
        "batch": state.entry_count,
        "pct": pct,
        "capital": capital,
        "qty": qty,
        "option_type": state.option_type,
        "strike": state.strike,
        "contracts": state.contracts,
        "avg_price": state.avg_price,
        "price": price,
    }

def close_position(state: PositionState) -> None:
    state.used_capital = 0.0
    state.entry_count = 0
    state.avg_price = 0.0
    state.size = 0.0
    state.option_type = ""
    state.strike = 0
    state.contracts = 0
