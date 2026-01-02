from __future__ import annotations
from trading_day import is_new_trading_day, reset_state_to_empty
from state_store import save_state
import time
from typing import Tuple

from ib_insync import IB

from config import (
    SYMBOL, BAR_SIZE, DURATION, USE_RTH,
    IB_HOST, IB_PORT, IB_CLIENT_ID,
    MAX_CAPITAL, ENTRY_LADDER,
    TAKE_PROFIT_PCT, STOP_LOSS_PCT, EXIT_RSI_LONG, EXIT_RSI_SHORT,
    STATE_FILE,
    APP_NAME, NOTIFY_COOLDOWN_SEC,
)

from data_ibkr import connect_ibkr, fetch_bars
from helper import use_rth_now
from indicators import add_indicators
from entry_rules import long_entry, short_entry
from exit_rules import should_exit_long, should_exit_short
from position import PositionState, try_open, close_position
from state_store import load_state, save_state, get_position, set_position
from session_params import load_params
from reminders import run_time_reminders
from notifier import (
    notify, NotifyConfig,
    format_title, format_message_entry, format_message_exit,
)


def _process_exit_and_entry(
    *,
    ib: IB,
    state,
    cfg: NotifyConfig,
    params,
    allow_long: bool,
    allow_short: bool,
) -> None:
    """
    单次循环：拉数据 -> 算指标 -> 先平仓 -> 再开仓 -> 落盘 state
    allow_long/allow_short 控制当次循环是否允许触发对应方向。
    """
    use_ruth = use_rth_now()
    df = fetch_bars(ib, SYMBOL, BAR_SIZE, DURATION, use_ruth)
    df = add_indicators(df)

    last = df.iloc[-1]
    close = float(last["close"])
    vwap = float(last["vwap"])
    rsi = float(last["rsi14"])
    ema9 = float(last["ema9"])
    bb_mid = float(last["bb_mid"])
    atr14 = float(last["atr14"])
    volume = float(last["volume"])

    print(f"RSI14: {rsi:.2f}, VWAP: {vwap:.2f}, CLOSE: {close:.2f}， EMA9: {ema9:.2f}, BB_MID: {bb_mid:.2f}, ATR14: {atr14:.2f}, volume: {volume:.2f}")

    long_pos = get_position(state, "long")
    short_pos = get_position(state, "short")

    # ---------- EXIT first ----------
    if long_pos.size > 0:
        ok, reason = should_exit_long(
            close=close, vwap=vwap, rsi14=rsi,
            avg_price=long_pos.avg_price,
            take_profit_pct=TAKE_PROFIT_PCT,
            stop_loss_pct=STOP_LOSS_PCT,
            exit_rsi_long=EXIT_RSI_LONG,
        )
        if ok and reason:
            title = format_title("EXIT", "LONG", SYMBOL, long_pos.strike, long_pos.contracts)
            msg = format_message_exit(last, long_pos.avg_price, long_pos.size, reason)
            notify(title, msg, cfg)
            close_position(long_pos)
            set_position(state, "long", long_pos)
            save_state(STATE_FILE, state)

    if short_pos.size > 0:
        ok, reason = should_exit_short(
            close=close, vwap=vwap, rsi14=rsi,
            avg_price=short_pos.avg_price,
            take_profit_pct=TAKE_PROFIT_PCT,
            stop_loss_pct=STOP_LOSS_PCT,
            exit_rsi_short=EXIT_RSI_SHORT,
        )
        if ok and reason:
            title = format_title("EXIT", "SHORT", SYMBOL, short_pos.strike, short_pos.contracts)
            msg = format_message_exit(last, short_pos.avg_price, short_pos.size, reason)
            notify(title, msg, cfg)
            close_position(short_pos)
            set_position(state, "short", short_pos)
            save_state(STATE_FILE, state)

    # ---------- ENTRY ----------
    # Guard: 不允许同时两边都开（如你要允许对冲/双持，去掉这个 guard）
    if allow_long and (short_pos.size <= 0) and long_entry(df):
        intent = try_open(True, close, long_pos)
        if intent:
            title = format_title("ENTRY", "LONG", SYMBOL, intent["strike"], intent["contracts"])
            msg = format_message_entry(last, intent)
            notify(title, msg, cfg)
            set_position(state, "long", long_pos)
            save_state(STATE_FILE, state)

    if allow_short and (long_pos.size <= 0) and short_entry(df):
        intent = try_open(True, close, short_pos)
        if intent:
            title = format_title("ENTRY", "SHORT", SYMBOL, intent["strike"], intent["contracts"])
            msg = format_message_entry(last, intent)
            notify(title, msg, cfg)
            set_position(state, "short", short_pos)
            save_state(STATE_FILE, state)


def run_trend_day_loop(*, state, cfg: NotifyConfig, poll_sec: int = 60) -> None:
    """
    趋势日：只顺势（bias=LONG/SHORT），NEUTRAL 则不做。
    open15_direction 如为 LONG/SHORT，优先级最高（覆盖 bias）。
    """
    last_fired = {}
    ib = connect_ibkr(IB_HOST, IB_PORT, IB_CLIENT_ID)
    try:
        while True:
            try:
                params = load_params("session_params.json")

                # 时间提醒（与你策略无关，照常发）
                run_time_reminders(last_fired, cfg)

                # ---- gating (TREND) ----
                allow_long = False
                allow_short = False

                # bias 决定方向
                if params.bias == "LONG":
                    allow_long = True
                elif params.bias == "SHORT":
                    allow_short = True

                # open15 override 优先级更高
                if params.open15_direction in ("LONG", "SHORT"):
                    allow_long = params.open15_direction == "LONG"
                    allow_short = params.open15_direction == "SHORT"

                _process_exit_and_entry(
                    ib=ib,
                    state=state,
                    cfg=cfg,
                    params=params,
                    allow_long=allow_long,
                    allow_short=allow_short,
                )
            except Exception as e:
                notify("⚠️ IBKR error", str(e)[:200], cfg)
                time.sleep(5)
            time.sleep(poll_sec)
    finally:
        ib.disconnect()


def run_range_day_loop(*, state, cfg: NotifyConfig, poll_sec: int = 60) -> None:
    """
    区间日：双向都允许（但仍保留“不同时双持”的 guard）。
    open15_direction 如为 LONG/SHORT，可以临时偏向一边（可选）。
    """
    last_fired = {}
    ib = connect_ibkr(IB_HOST, IB_PORT, IB_CLIENT_ID)
    try:
        while True:
            try:
                params = load_params("session_params.json")

                # 时间提醒
                run_time_reminders(last_fired, cfg)

                # ---- gating (RANGE) ----
                allow_long = True
                allow_short = True

                # 如果你希望开盘15分钟判定后只做一边，打开这个 override：
                if params.open15_direction in ("LONG", "SHORT"):
                    allow_long = params.open15_direction == "LONG"
                    allow_short = params.open15_direction == "SHORT"

                _process_exit_and_entry(
                    ib=ib,
                    state=state,
                    cfg=cfg,
                    params=params,
                    allow_long=allow_long,
                    allow_short=allow_short,
                )
            except Exception as e:
                notify("⚠️ IBKR error", str(e)[:200], cfg)
                time.sleep(5)
            time.sleep(poll_sec)
    finally:
        ib.disconnect()


def main(poll_sec: int = 60) -> None:
    cfg = NotifyConfig(app_name=APP_NAME, cooldown_sec=NOTIFY_COOLDOWN_SEC)

    long_default = PositionState("long", MAX_CAPITAL, ENTRY_LADDER)
    short_default = PositionState("short", MAX_CAPITAL, ENTRY_LADDER)
    state = load_state(STATE_FILE, long_default, short_default)
    if is_new_trading_day(state):
        state = reset_state_to_empty(state)
        save_state(STATE_FILE, state)

    # 只在启动时选一次模式；你如果想“盘中切换 day_type”，我也可以改成每次循环都判断并跳转
    params = load_params("session_params.json")
    day_type = str(getattr(params, "day_type", "RANGE")).upper()

    print(f"state: {state}")

    if day_type == "TREND":
        run_trend_day_loop(state=state, cfg=cfg, poll_sec=poll_sec)
    else:
        run_range_day_loop(state=state, cfg=cfg, poll_sec=poll_sec)


if __name__ == "__main__":
    main(poll_sec=60)
