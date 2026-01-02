# trading_day.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo  # Python 3.9+

def _et_today_str(now: datetime | None = None, tz_name: str = "America/New_York") -> str:
    tz = ZoneInfo(tz_name)
    now = now or datetime.now(tz=tz)
    if now.tzinfo is None:
        now = now.replace(tzinfo=tz)
    return now.astimezone(tz).strftime("%Y-%m-%d")

def is_new_trading_day(state: dict, tz_name: str = "America/New_York") -> bool:
    """
    Return True if the saved state is from a different ET calendar date.
    - We store/compare `state["_meta"]["trading_date_et"]` as YYYY-MM-DD.
    - Weekend handling: If program didn't run during weekend, Monday will differ -> True (good).
    """
    today = _et_today_str(tz_name=tz_name)
    saved = (
        state.get("_meta", {}).get("trading_date_et")
        or state.get("meta", {}).get("trading_date_et")  # compatibility if you named it "meta"
        or ""
    )
    return saved != today

def reset_state_to_empty(state: dict, tz_name: str = "America/New_York") -> dict:
    """
    Reset runtime position fields to empty, keeping max_capital and ladder as-is.
    Also sets meta trading date to today's ET date.
    Works for both long/short positions.
    """
    for side in ("long", "short"):
        if side not in state:
            continue

        pos = state[side]

        # Keep these configs
        # - direction, max_capital, ladder: keep
        # Reset runtime fields
        pos["used_capital"] = 0.0
        pos["entry_count"] = 0
        pos["avg_price"] = 0.0
        pos["size"] = 0.0
        pos["stopped_today"] = False

        # Option fields (notification-only in your current design)
        pos["option_type"] = ""
        pos["strike"] = 0
        pos["contracts"] = 0

    tz = ZoneInfo(tz_name)
    today_et = datetime.now(tz=tz).strftime("%Y-%m-%d")
    state.setdefault("_meta", {})
    state["_meta"]["trading_date_et"] = today_et
    state["_meta"]["tz"] = tz_name
    state["_meta"]["reset_at_et"] = datetime.now(tz=tz).strftime("%Y-%m-%d %H:%M:%S")

    return state
