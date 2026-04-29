import os

# ── STOCKS TO TRACK ───────────────────────────────────────
STOCKS = [
    "IVV",
    "VTI",
    "VGS.AX",
]

# ── EMAIL SETTINGS ────────────────────────────────────────
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "jasondylanhassard@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "toftrkkbazgwycof")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER", "jasondylanhassard@gmail.com,matthewbrosnan8@gmail.com").split(",")

# ── SCORING THRESHOLDS ────────────────────────────────────
PE_LOW = 20
PE_HIGH = 30
MA_SHORT = 50
MA_LONG = 200
WEEK_LOW_THRESHOLD = 0.3
WEEK_HIGH_THRESHOLD = 0.8
BUY_SCORE = 4
HOLD_SCORE = 2