IBKR RSI/VWAP Signal + Notifications (ENTRY green, EXIT blue)
===========================================================

What it does
------------
- Pull bars from Interactive Brokers (IBKR) via ib_insync
- Compute RSI(14) + VWAP
- Generate ENTRY signals (LONG/SHORT) with staged sizing
- Track a simple paper position state in `state.json`
- Generate EXIT signals (profit/stop + mean-reversion exit)
- Notify via:
  - Terminal banner + beep (always)
  - macOS banner via `terminal-notifier` (if installed)
  - Telegram message (if TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID are set)

Install
-------
pip install ib_insync pandas pandas_ta requests

Optional (macOS popup):
brew install terminal-notifier

Telegram (recommended)
---------------------
export TELEGRAM_BOT_TOKEN="123:abc..."
export TELEGRAM_CHAT_ID="8166...."

Run
---
python main.py

Notes
-----
- This project does NOT place orders by default.
- EXIT logic is a starter template; tune thresholds in config.py.


Session parameters
------------------
- Edit `session_params.json` with the values you get from the two prompts.
- Program reads it every loop.

Daemon loop & reminders
----------------------
- `main.py` runs in a loop (default 60s poll) and fires reminders at 6:30, 9:30, 11:00 (machine local time).
