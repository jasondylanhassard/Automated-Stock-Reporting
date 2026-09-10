import pandas as pd
import os
from datetime import datetime

PORTFOLIO_FILE = "portfolio.csv"

COLUMNS = [
    "ticker",
    "buy_date",
    "buy_price",
    "quantity",
    "status",       # open or closed
    "sell_price",
    "sell_date",
]

def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(PORTFOLIO_FILE, index=False)
    return pd.read_csv(PORTFOLIO_FILE)

def add_position(ticker, buy_date, buy_price, quantity):
    df = load_portfolio()
    new_row = {
        "ticker": ticker.upper(),
        "buy_date": buy_date,
        "buy_price": float(buy_price),
        "quantity": float(quantity),
        "status": "open",
        "sell_price": None,
        "sell_date": None,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(PORTFOLIO_FILE, index=False)
    print(f"✅ Added {ticker} position")

def close_position(index, sell_price, sell_date=None):
    df = load_portfolio()
    if sell_date is None:
        sell_date = datetime.today().strftime("%Y-%m-%d")
    df.at[index, "status"] = "closed"
    df.at[index, "sell_price"] = float(sell_price)
    df.at[index, "sell_date"] = sell_date
    df.to_csv(PORTFOLIO_FILE, index=False)
    print(f"✅ Closed position at ${sell_price}")

def get_open_positions():
    df = load_portfolio()
    return df[df["status"] == "open"].copy()

def get_closed_positions():
    df = load_portfolio()
    return df[df["status"] == "closed"].copy()

def calculate_realised_pnl():
    closed = get_closed_positions()
    if closed.empty:
        return 0.0
    closed["pnl"] = (closed["sell_price"] - closed["buy_price"]) * closed["quantity"]
    return closed["pnl"].sum()
