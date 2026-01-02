from __future__ import annotations

# -------------------------
# Message templates (Telegram/macOS banner)
# -------------------------

def _fmt_money(x) -> str:
    try:
        return f"${float(x):,.0f}"
    except Exception:
        return str(x)

def _fmt_pct(p) -> str:
    try:
        return f"{float(p)*100:.0f}%"
    except Exception:
        return str(p)

def _format_entry_message(intent: dict) -> tuple[str, str]:
    """Return (title, body) for ENTRY notifications."""
    side = (intent.get("direction") or "").upper()
    symbol = intent.get("symbol", "")
    strike = intent.get("strike", "")
    qty = intent.get("qty", intent.get("contracts", 1))

    # Title requirement from you: Long QQQ @ Strike * quantity
    title = f"{side.capitalize()} {symbol} @ {strike} x{qty}"

    # Optional icon by batch (1..4)
    batch_icon = {1:"🟢", 2:"🟡", 3:"🟠", 4:"🔴"}.get(int(intent.get("batch", 0) or 0), "")
    if batch_icon:
        title = f"{batch_icon} {title}"

    price = intent.get("price")
    vwap  = intent.get("vwap")
    rsi14 = intent.get("rsi14")
    ema9  = intent.get("ema9")
    bbmid = intent.get("bbmid")
    atr14 = intent.get("atr14")

    cv_tag = intent.get("cv_tag", "")  # optional e.g. "(C<V)" passed by signal code

    body_lines = [
        f"Option: {intent.get('option_label', '').strip() or (side + ' ' + str(intent.get('option_type','')).strip()).strip()}",
        f"Underlying: {float(price):.2f}" if price is not None else "Underlying: -",
        f"Strike: {strike} | Qty: {qty}",
        f"Batch: {intent.get('batch')} / {_fmt_pct(intent.get('pct'))} | Capital: {_fmt_money(intent.get('capital'))}",
        "",
        f"RSI14: {float(rsi14):.2f}" if rsi14 is not None else "RSI14: -",
        f"VWAP:  {float(vwap):.2f} {cv_tag}".rstrip() if vwap is not None else "VWAP:  -",
    ]

    # Add extra indicators if present
    extras = []
    if ema9 is not None:  extras.append(f"EMA9: {float(ema9):.2f}")
    if bbmid is not None: extras.append(f"BBmid: {float(bbmid):.2f}")
    if atr14 is not None: extras.append(f"ATR14: {float(atr14):.2f}")
    if extras:
        body_lines.append(" | ".join(extras))

    return title, "\n".join(body_lines).strip()

def _format_exit_message(intent: dict) -> tuple[str, str]:
    """Return (title, body) for EXIT notifications."""
    side = (intent.get("direction") or "").upper()
    symbol = intent.get("symbol", "")
    strike = intent.get("strike", "")
    qty = intent.get("qty", intent.get("contracts", 1))
    reason = intent.get("reason", "EXIT")
    title = f"🔵 {reason}: {side.capitalize()} {symbol} @ {strike} x{qty}"

    price = intent.get("price")
    avg = intent.get("avg_price")
    pnl = intent.get("pnl_pct")

    body_lines = [
        f"Reason: {reason}",
        f"Underlying: {float(price):.2f}" if price is not None else "Underlying: -",
        f"Avg(U): {float(avg):.2f}" if avg is not None else "Avg(U): -",
        f"PnL: {float(pnl)*100:.2f}%" if pnl is not None else "PnL: -",
    ]
    return title, "\n".join(body_lines).strip()

import os
import sys
import time
import subprocess
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class NotifyConfig:
    app_name: str = "IBKR Signal"
    cooldown_sec: int = 10


_last_sent_ts: float = 0.0


# Event icons: ENTRY green, EXIT blue
EVENT_ICON = {
    "ENTRY": "🟢",
    "EXIT":  "🔵",
    "STOP":  "🔴",
    "INFO":  "🟡",
}


def _beep() -> None:
    try:
        sys.stdout.write("\a")
        sys.stdout.flush()
    except Exception:
        pass


def _terminal_banner(title: str, message: str, app_name: str) -> None:
    line = "=" * 72
    print("\n" + line, flush=True)
    print(f"[{app_name}] {title}", flush=True)
    print(message, flush=True)
    print(line + "\n", flush=True)


def _mac_banner(title: str, message: str, app_name: str) -> None:
    try:
        subprocess.run([
            "terminal-notifier",
            "-sender", "com.apple.Terminal",  # 让通知归属到 Terminal
            "-title", title,
            #"-subtitle", app_name,
            "-message", message.replace("\n", " | "),
        ], check=False)
    except Exception:
        pass


def _telegram_send(title: str, message: str, app_name: str) -> bool:
    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    chat_id = (os.getenv("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat_id:
        return False

    one_line = message.replace("\n", " | ")
    text = f"{title}\n{one_line}"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def notify(title: str, message: str, cfg: Optional[NotifyConfig] = None) -> None:
    global _last_sent_ts
    cfg = cfg or NotifyConfig()

    now = time.time()
    if now - _last_sent_ts < cfg.cooldown_sec:
        return
    _last_sent_ts = now

    _terminal_banner(title, message, cfg.app_name)
    _beep()
    _mac_banner(title, message, cfg.app_name)
    _telegram_send(title, message, cfg.app_name)


def format_title(event: str, side: str, symbol: str, strike: int, contracts: int) -> str:
    """Title spec: Long QQQ @ Strike x quantity (contracts)."""
    icon = EVENT_ICON.get(event.upper(), "")
    return f"{icon} {side.upper()} {symbol} @ {int(strike)} x{int(contracts)}"



def format_message_entry(last_row, intent: dict) -> str:
    under = float(intent["price"])
    vwap = float(last_row["vwap"])
    rsi = float(last_row["rsi14"])
    ema9 = float(last_row["ema9"]) if ("ema9" in last_row and last_row["ema9"] is not None) else float("nan")
    bb_mid = float(last_row["bb_mid"]) if ("bb_mid" in last_row and last_row["bb_mid"] is not None) else float("nan")
    atr14 = float(last_row["atr14"]) if ("atr14" in last_row and last_row["atr14"] is not None) else float("nan")
    cv = "C<V" if under < vwap else "C>V"
    return (
        f"Option: LONG {intent.get('option_type', '?')}  Strike: {intent.get('strike', 0)}  Qty: {intent.get('contracts', 0)}\n"
        f"Underlying: {under:.2f} | VWAP: {vwap:.2f} ({cv}) | RSI14: {rsi:.2f}\n"
        f"EMA9: {ema9:.2f} | BBmid: {bb_mid:.2f} | ATR14: {atr14:.2f}\n"
        f"Batch: {intent['batch']} / {int(intent['pct']*100)}%  Capital: ${intent['capital']:.0f}  Avg(U): {intent['avg_price']:.2f}"
    )


def format_message_exit(last_row, avg_price: float, size: float, reason: str) -> str:
    close = float(last_row["close"])
    vwap = float(last_row["vwap"])
    rsi = float(last_row["rsi14"])
    ema9 = float(last_row["ema9"]) if ("ema9" in last_row and last_row["ema9"] is not None) else float("nan")
    bb_mid = float(last_row["bb_mid"]) if ("bb_mid" in last_row and last_row["bb_mid"] is not None) else float("nan")
    atr14 = float(last_row["atr14"]) if ("atr14" in last_row and last_row["atr14"] is not None) else float("nan")
    cv = "C<V" if close < vwap else "C>V"
    pnl = (close - avg_price) * size
    return (
        f"Reason: {reason}\n"
        f"Close: {close:.2f} | Avg: {avg_price:.2f} | PnL($): {pnl:.2f}\n"
        f"RSI14: {rsi:.2f} | VWAP: {vwap:.2f} ({cv})\n"
        f"EMA9: {ema9:.2f} | BBmid: {bb_mid:.2f} | ATR14: {atr14:.2f}\n"
        f"Qty(shares): {size:.4f}"
    )


def send_telegram_message(title: str, body: str) -> None:
    """Send Telegram notification with a title + body (body can be multiline)."""
    text = f"{title}\n\n{body}".strip()
    send_telegram(text)



def notify_entry(intent: dict) -> None:
    title, body = _format_entry_message(intent)
    send_telegram_message(title, body)

def notify_exit(intent: dict) -> None:
    title, body = _format_exit_message(intent)
    send_telegram_message(title, body)
