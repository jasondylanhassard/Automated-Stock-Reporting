import yfinance as yf
from config import STOCKS, MA_SHORT, MA_LONG

def fetch_stock_data(ticker):
    print(f"Fetching data for {ticker}...")

    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="1y")

    # More robust price fetching for ASX stocks
    current_price = hist["Close"].iloc[-1] if len(hist) > 0 else None

    week_high = info.get("fiftyTwoWeekHigh") or (hist["Close"].max() if len(hist) > 0 else None)
    week_low = info.get("fiftyTwoWeekLow") or (hist["Close"].min() if len(hist) > 0 else None)
    pe_ratio = info.get("trailingPE", None)

    # Use hist close prices for change calculations to avoid bad info data
    price_1d_ago = hist["Close"].iloc[-2] if len(hist) >= 2 else current_price
    price_1w_ago = hist["Close"].iloc[-6] if len(hist) >= 6 else current_price
    price_1m_ago = hist["Close"].iloc[-22] if len(hist) >= 22 else current_price
    price_3m_ago = hist["Close"].iloc[-66] if len(hist) >= 66 else current_price

    # Use hist close for current price in change calculations for consistency
    hist_current = hist["Close"].iloc[-1] if len(hist) > 0 else current_price

    change_1d = ((hist_current - price_1d_ago) / price_1d_ago) * 100
    change_1w = ((hist_current - price_1w_ago) / price_1w_ago) * 100
    change_1m = ((hist_current - price_1m_ago) / price_1m_ago) * 100
    change_3m = ((hist_current - price_3m_ago) / price_3m_ago) * 100

    ma_short = hist["Close"].tail(MA_SHORT).mean()
    ma_long = hist["Close"].tail(MA_LONG).mean()

    return {
        "ticker": ticker,
        "current_price": current_price,
        "change_1d": round(change_1d, 2),
        "change_1w": round(change_1w, 2),
        "change_1m": round(change_1m, 2),
        "change_3m": round(change_3m, 2),
        "52w_high": week_high,
        "52w_low": week_low,
        "pe_ratio": pe_ratio,
        "ma_short": round(ma_short, 2),
        "ma_long": round(ma_long, 2),
    }

def fetch_all_stocks():
    return [fetch_stock_data(ticker) for ticker in STOCKS]
