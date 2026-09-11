import os

# ── STOCKS TO TRACK ───────────────────────────────────────
STOCKS = [
    "IVV",
    "VTI",
    "VGS.AX",
    "VAS.AX",
    "VTS.AX",
    "MIN.AX",
    "NVDA",
    "PLS.AX",
    "LRV.AX",
    "PLTR",
    "TOPT",
    "TSM",
    "VTM.AX",
    "PMGOLD.AX",
]

# ── EMAIL SETTINGS ────────────────────────────────────────
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "jasondylanhassard@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "toftrkkbazgwycof")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER", "jasondylanhassard@gmail.com").split(",")

# ── SCORING THRESHOLDS ────────────────────────────────────
PE_LOW = 20
PE_HIGH = 30
MA_SHORT = 50
MA_LONG = 200
WEEK_LOW_THRESHOLD = 0.3
WEEK_HIGH_THRESHOLD = 0.8
BUY_SCORE = 4
HOLD_SCORE = 2


GITHUB_TOKEN = os.environ.get("DB_TOKEN", "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")
GITHUB_REPO = "jasondylanhassard/Automated-Stock-Reporting"
GITHUB_FILE = "portfolio.csv"
DASHBOARD_URL = "https://automated-stock-reporting-5ssvjzmxpdnktrhiommmz5.streamlit.app/"