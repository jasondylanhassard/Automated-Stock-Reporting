import os

# ── STOCKS TO TRACK ───────────────────────────────────────
STOCKS = [
    "IVV",    # iShares S&P 500 ETF
    "VTI",    # Vanguard Total Stock Market ETF
    "VGS.AX", # Vanguard Global Shares (ASX listed)
]

# ── EMAIL SETTINGS ────────────────────────────────────────
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "jasondylanhassard@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "your_app_password")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER", "jasondylanhassard@gmail.com,matthewbrosnan8@gmail.com").split(",")

# ── SCORING THRESHOLDS ────────────────────────────────────
PE_LOW = 20       # Below this = good (cheap)
PE_HIGH = 30      # Above this = expensive

MA_SHORT = 50     # 50-day moving average
MA_LONG = 200     # 200-day moving average

WEEK_LOW_THRESHOLD = 0.3   # Bottom 30% of 52-week range = good entry
WEEK_HIGH_THRESHOLD = 0.8  # Top 20% of 52-week range = caution

# ── VERDICT THRESHOLDS ────────────────────────────────────
BUY_SCORE = 4     # Score 4+ = Buy
HOLD_SCORE = 2    # Score 2-3 = Hold
                  # Below 2 = Sell