import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
from portfolio import (
    load_portfolio,
    add_position,
    close_position,
    get_open_positions,
    get_closed_positions,
    calculate_realised_pnl,
)
from config import STOCKS

st.set_page_config(page_title="Stock Dashboard", page_icon="📈", layout="wide")
st.title("📈 Stock Portfolio Dashboard")

# ── SIDEBAR — ADD POSITION ─────────────────────────────────
st.sidebar.header("Add New Position")
ticker_input = st.sidebar.selectbox("Ticker", sorted(STOCKS))
buy_date = st.sidebar.date_input("Buy Date", value=date.today())
buy_price = st.sidebar.number_input("Buy Price ($)", min_value=0.01, step=0.01)
quantity = st.sidebar.number_input("Quantity (units)", min_value=0.01, step=1.0)

if st.sidebar.button("Add Position"):
    if buy_price > 0 and quantity > 0:
        add_position(ticker_input, str(buy_date), buy_price, quantity)
        st.sidebar.success(f"Added {ticker_input}!")
        st.write("DEBUG — Current portfolio:")
        st.write(load_portfolio())
        st.rerun()
    else:
        st.sidebar.error("Please enter a valid price and quantity")

# ── OPEN POSITIONS ─────────────────────────────────────────
st.header("📂 Open Positions")

open_pos = get_open_positions()

if open_pos.empty:
    st.info("No open positions yet — add one in the sidebar!")
else:
    rows = []
    for idx, row in open_pos.iterrows():
        try:
            hist = yf.Ticker(row["ticker"]).history(period="5d")
            current_price = hist["Close"].iloc[-1] if len(hist) > 0 else row["buy_price"]
        except:
            current_price = row["buy_price"]

        pnl_per_unit = current_price - row["buy_price"]
        pnl_total = pnl_per_unit * row["quantity"]
        pnl_pct = (pnl_per_unit / row["buy_price"]) * 100
        market_value = current_price * row["quantity"]
        cost_basis = row["buy_price"] * row["quantity"]

        rows.append({
            "idx": idx,
            "Ticker": row["ticker"],
            "Buy Date": row["buy_date"],
            "Buy Price": f"${row['buy_price']:.2f}",
            "Current Price": f"${current_price:.2f}",
            "Quantity": row["quantity"],
            "Market Value": f"${market_value:.2f}",
            "P&L $": f"${pnl_total:+.2f}",
            "P&L %": f"{pnl_pct:+.2f}%",
        })

    display_df = pd.DataFrame(rows).drop(columns=["idx"])

    def color_pnl(val):
        if isinstance(val, str) and val.startswith("$"):
            num = float(val.replace("$", "").replace("+", ""))
            color = "green" if num >= 0 else "red"
            return f"color: {color}"
        if isinstance(val, str) and val.endswith("%"):
            num = float(val.replace("%", "").replace("+", ""))
            color = "green" if num >= 0 else "red"
            return f"color: {color}"
        return ""

    st.dataframe(
        display_df.style.map(color_pnl, subset=["P&L $", "P&L %"]),
        use_container_width=True
    )

    # ── CLOSE A POSITION ──────────────────────────────────
    st.subheader("Close a Position")
    open_labels = [f"{r['Ticker']} (bought {r['Buy Date']} @ {r['Buy Price']})" for r in rows]
    selected = st.selectbox("Select position to close", open_labels)
    sell_price = st.number_input("Sell Price ($)", min_value=0.01, step=0.01, key="sell")
    sell_date = st.date_input("Sell Date", value=date.today(), key="sell_date")

    if st.button("Close Position"):
        selected_idx = rows[open_labels.index(selected)]["idx"]
        close_position(selected_idx, sell_price, str(sell_date))
        st.success("Position closed!")
        st.rerun()

# ── PORTFOLIO SUMMARY ──────────────────────────────────────
st.header("💰 Portfolio Summary")

col1, col2, col3 = st.columns(3)

if not open_pos.empty:
    total_cost = sum(r["buy_price"] * r["quantity"] for _, r in open_pos.iterrows())
    col1.metric("Total Cost Basis", f"${total_cost:,.2f}")

realised = calculate_realised_pnl()
col2.metric("Realised P&L (lifetime)", f"${realised:+,.2f}", delta_color="normal")

# ── CLOSED POSITIONS ───────────────────────────────────────
st.header("✅ Closed Positions")
closed = get_closed_positions()

if closed.empty:
    st.info("No closed positions yet")
else:
    closed["P&L $"] = (closed["sell_price"] - closed["buy_price"]) * closed["quantity"]
    closed["P&L %"] = ((closed["sell_price"] - closed["buy_price"]) / closed["buy_price"]) * 100
    st.dataframe(closed, use_container_width=True)

# ── PRICE CHART ────────────────────────────────────────────
st.header("📊 Price Chart")

chart_ticker = st.selectbox("Select ticker to chart", sorted(STOCKS), key="chart")
period = st.radio("Period", ["1mo", "3mo", "6mo", "1y", "5y"], horizontal=True)

hist = yf.Ticker(chart_ticker).history(period=period)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist["Close"],
    mode="lines",
    name=chart_ticker,
    line=dict(color="#1a1a2e", width=2)
))

# Plot buy points for this ticker
if not open_pos.empty:
    ticker_positions = open_pos[open_pos["ticker"] == chart_ticker]
    for _, pos in ticker_positions.iterrows():
        fig.add_trace(go.Scatter(
            x=[pos["buy_date"]],
            y=[pos["buy_price"]],
            mode="markers+text",
            marker=dict(color="green", size=12, symbol="triangle-up"),
            text=["BUY"],
            textposition="top center",
            name=f"Bought @ ${pos['buy_price']:.2f}"
        ))

# Plot sell points for this ticker
if not closed.empty:
    ticker_closed = closed[closed["ticker"] == chart_ticker]
    for _, pos in ticker_closed.iterrows():
        fig.add_trace(go.Scatter(
            x=[pos["sell_date"]],
            y=[pos["sell_price"]],
            mode="markers+text",
            marker=dict(color="red", size=12, symbol="triangle-down"),
            text=["SELL"],
            textposition="bottom center",
            name=f"Sold @ ${pos['sell_price']:.2f}"
        ))

fig.update_layout(
    title=f"{chart_ticker} Price Chart",
    xaxis_title="Date",
    yaxis_title="Price ($)",
    template="plotly_white",
    height=500
)

st.plotly_chart(fig, use_container_width=True)