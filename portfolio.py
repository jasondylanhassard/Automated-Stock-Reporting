import pandas as pd
import base64
import requests
import io
from datetime import datetime
from config import GITHUB_TOKEN, GITHUB_REPO, GITHUB_FILE

COLUMNS = [
    "ticker",
    "buy_date", 
    "buy_price",
    "quantity",
    "status",
    "sell_price",
    "sell_date",
]

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_file_from_github():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 404:
        return pd.DataFrame(columns=COLUMNS), None
    data = response.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    df = pd.read_csv(io.StringIO(content))
    return df, data["sha"]

def push_file_to_github(df, sha=None, message="Update portfolio"):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    content = base64.b64encode(df.to_csv(index=False).encode()).decode()
    payload = {
        "message": message,
        "content": content,
    }
    if sha:
        payload["sha"] = sha
    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code in [200, 201]:
        print("✅ Portfolio synced to GitHub!")
    else:
        print(f"❌ GitHub sync failed: {response.status_code} {response.text}")

def load_portfolio():
    df, _ = get_file_from_github()
    return df

def add_position(ticker, buy_date, buy_price, quantity):
    df, sha = get_file_from_github()
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
    push_file_to_github(df, sha, message=f"Add {ticker} position")
    print(f"✅ Added {ticker} position")

def close_position(index, sell_price, sell_date=None):
    df, sha = get_file_from_github()
    if sell_date is None:
        sell_date = datetime.today().strftime("%Y-%m-%d")
    df.at[index, "status"] = "closed"
    df.at[index, "sell_price"] = float(sell_price)
    df.at[index, "sell_date"] = sell_date
    push_file_to_github(df, sha, message=f"Close position at ${sell_price}")
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