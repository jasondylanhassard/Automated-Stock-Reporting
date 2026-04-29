import yfinance as yf
from config import STOCKS, MA_SHORT, MA_LONG

def fetch_stock_data(ticker):
    """Fetches all raw data needed for scoring from Yahoo Finance."""
    
    print(f"Fetching data for {ticker}...")
    
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="200d")

    current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
    week_high = info.get("fiftyTwoWeekHigh", 0)
    week_low = info.get("fiftyTwoWeekLow", 0)
    pe_ratio = info.get("trailingPE", None)

    ma_short = hist["Close"].tail(MA_SHORT).mean()
    ma_long = hist["Close"].tail(MA_LONG).mean()

    return {
        "ticker": ticker,
        "current_price": current_price,
        "52w_high": week_high,
        "52w_low": week_low,
        "pe_ratio": pe_ratio,
        "ma_short": round(ma_short, 2),
        "ma_long": round(ma_long, 2),
    }

def fetch_all_stocks():
    """Loops through all stocks in config and returns a list of data."""
    return [fetch_stock_data(ticker) for ticker in STOCKS]