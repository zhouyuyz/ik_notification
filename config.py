# ---- Market data / symbol ----
SYMBOL = "QQQ"
BAR_SIZE = "5 mins"      # e.g. "5 mins", "15 mins"
DURATION = "1 D"         # e.g. "1 D", "2 D"
USE_RTH = False           # True=regular hours only, False=include extended, time based use_ruth is using in the code

# ---- IBKR connection ----
IB_HOST = "127.0.0.1"
IB_PORT = 7496           # TWS paper: 7497, TWS live: 7496, Gateway paper: 4002, Gateway live: 4001
IB_CLIENT_ID = 88

# ---- Risk / sizing (paper sizing) ----
MAX_CAPITAL = 9000.0                 # max capital allocated to ONE direction (long OR short)
ENTRY_LADDER = [0.3, 0.2, 0.4, 0.1]   # staged entries: 30/20/40/10

# ---- Exit rules (starter template) ----
TAKE_PROFIT_PCT = 0.012   # +1.2% from avg => EXIT
STOP_LOSS_PCT   = 0.008   # -0.8% from avg => EXIT
EXIT_RSI_LONG   = 55      # for long: RSI>=55 AND C>VWAP => EXIT
EXIT_RSI_SHORT  = 45      # for short: RSI<=45 AND C<VWAP => EXIT

# ---- State persistence ----
STATE_FILE = "state.json"   # saved in working directory

# INDICATOR

RSI_LENGTH = 14
RSI_MODE = "rma"

# ---- Notification ----
APP_NAME = "IBKR Signal"
NOTIFY_COOLDOWN_SEC = 10     # prevent spam (applies to all channels)

# Telegram: set via env vars
#   TELEGRAM_BOT_TOKEN
#   TELEGRAM_CHAT_ID
