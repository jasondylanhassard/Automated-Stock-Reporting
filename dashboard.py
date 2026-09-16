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

# ── THEME ──────────────────────────────────────────────────
st.set_page_config(page_title="ASR Platform", page_icon=None, layout="wide")

st.markdown("""
<style>
    /* Global */
    html, body, [class*="css"] {
        background-color: #0d0d0d;
        color: #e8e8e8;
        font-family: Arial, sans-serif;
    }
    .stApp { background-color: #0d0d0d; }

    /* Header */
    .main-header {
        border-bottom: 1px solid #00c47a;
        padding-bottom: 16px;
        margin-bottom: 32px;
    }
    .platform-name {
        color: #00c47a;
        font-size: 11px;
        letter-spacing: 3px;
        font-weight: 700;
    }
    .report-title {
        color: #e8e8e8;
        font-size: 22px;
        font-weight: 600;
        letter-spacing: 1px;
        margin: 8px 0 4px 0;
    }
    .report-subtitle {
        color: #666;
        font-size: 11px;
        letter-spacing: 1px;
    }

    /* Section labels */
    .section-label {
        color: #00c47a;
        font-size: 11px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
        margin-top: 32px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #1a1a1a;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label {
        color: #e8e8e8 !important;
        font-size: 11px !important;
        letter-spacing: 1px !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: transparent;
        border: 1px solid #00c47a;
        color: #00c47a;
        font-size: 11px;
        letter-spacing: 2px;
        border-radius: 2px;
        padding: 8px 20px;
    }
    .stButton > button:hover {
        background-color: #00c47a;
        color: #0d0d0d;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background-color: #141414;
        border: 1px solid #1a1a1a;
        padding: 16px;
        border-radius: 2px;
    }
    [data-testid="stMetricLabel"] { color: #666 !important; font-size: 11px !important; letter-spacing: 1px !important; }
    [data-testid="stMetricValue"] { color: #e8e8e8 !important; font-family: monospace !important; }

    /* Dataframe */
    [data-testid="stDataFrame"] { border: 1px solid #1a1a1a; }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────
now = datetime.now().strftime("%d %B %Y  |  %H:%M AEST")
st.markdown(f"""
<div class="main-header">
    <div class="platform-name">ASR PLATFORM</div>
    <div class="report-title">Portfolio Management</div>
    <div class="report-subtitle">AUTOMATED MARKET INTELLIGENCE &nbsp;|&nbsp; {now}</div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR — ADD POSITION ─────────────────────────────────
st.sidebar.markdown("<div class='platform-name' style='margin-bottom:16px'>NEW POSITION</div>", unsafe_allow_html=True)
ticker_input = st.sidebar.selectbox("Ticker", sorted(STOCKS), label_visibility="visible")
buy_date = st.sidebar.date_input("Entry Date", value=date.today())
buy_price = st.sidebar.number_input("Entry Price ($)", min_value=0.01, step=0.01)
quantity = st.sidebar.number_input("Quantity", min_value=0.01, step=1.0)

if st.sidebar.button("SUBMIT POSITION"):
    if buy_price > 0 and quantity > 0:
        add_position(ticker_input, str(buy_date), buy_price, quantity)
        st.sidebar.success(f"{ticker_input} position recorded.")
        st.rerun()
    else:
        st.sidebar.error("Invalid entry price or quantity.")

st.sidebar.markdown("<hr style='border-color:#1a1a1a;margin:24px 0'>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='platform-name' style='margin-bottom:16px'>CLOSE POSITION</div>", unsafe_allow_html=True)

# ── OPEN POSITIONS ─────────────────────────────────────────
st.markdown("<div class='section-label'>Open Positions</div>", unsafe_allow_html=True)

open_pos = get_open_positions()

if open_pos.empty:
    st.markdown(f"<p style='color:#666;font-size:13px'>No open positions on record.</p>", unsafe_allow_html=True)
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

        rows.append({
            "idx": idx,
            "Ticker": row["ticker"],
            "Entry Date": row["buy_date"],
            "Entry Price": f"{row['buy_price']:.2f}",
            "Current": f"{current_price:.2f}",
            "Qty": f"{row['quantity']:.0f}",
            "Mkt Value": f"{market_value:.2f}",
            "P/L $": f"{pnl_total:+.2f}",
            "P/L %": f"{pnl_pct:+.2f}%",
        })

    display_df = pd.DataFrame(rows).drop(columns=["idx"])

    def color_pnl(val):
        try:
            num = float(str(val).replace("+", "").replace("%", ""))
            return "color: #00c47a" if num >= 0 else "color: #e03e3e"
        except:
            return ""

    st.dataframe(
        display_df.style.map(color_pnl, subset=["P/L $", "P/L %"]),
        use_container_width=True,
        hide_index=True
    )

    # ── CLOSE POSITION IN SIDEBAR ─────────────────────────
    open_labels = [f"{r['Ticker']}  —  entry {r['Entry Date']}  @  {r['Entry Price']}" for r in rows]
    selected = st.sidebar.selectbox("Select Position", open_labels)
    sell_price = st.sidebar.number_input("Exit Price ($)", min_value=0.01, step=0.01, key="sell")
    sell_date = st.sidebar.date_input("Exit Date", value=date.today(), key="sell_date")

    if st.sidebar.button("CLOSE POSITION"):
        selected_idx = rows[open_labels.index(selected)]["idx"]
        close_position(selected_idx, sell_price, str(sell_date))
        st.sidebar.success("Position closed.")
        st.rerun()

# ── PORTFOLIO SUMMARY ──────────────────────────────────────
st.markdown("<div class='section-label'>Portfolio Summary</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

if not open_pos.empty:
    total_cost = sum(row["buy_price"] * row["quantity"] for _, row in open_pos.iterrows())
    col1.metric("Cost Basis", f"${total_cost:,.2f}")

realised = calculate_realised_pnl()
col2.metric("Realised P/L", f"${realised:+,.2f}")

# ── CLOSED POSITIONS ───────────────────────────────────────
st.markdown("<div class='section-label'>Closed Positions</div>", unsafe_allow_html=True)
closed = get_closed_positions()

if closed.empty:
    st.markdown("<p style='color:#666;font-size:13px'>No closed positions on record.</p>", unsafe_allow_html=True)
else:
    closed["P/L $"] = (closed["sell_price"] - closed["buy_price"]) * closed["quantity"]
    closed["P/L %"] = ((closed["sell_price"] - closed["buy_price"]) / closed["buy_price"]) * 100
    st.dataframe(closed, use_container_width=True, hide_index=True)

# ── PRICE CHART ────────────────────────────────────────────
st.markdown("<div class='section-label'>Price Chart</div>", unsafe_allow_html=True)

col_a, col_b = st.columns([2, 5])
with col_a:
    chart_ticker = st.selectbox("Instrument", sorted(STOCKS), key="chart", label_visibility="collapsed")
with col_b:
    period = st.radio("Period", ["1mo", "3mo", "6mo", "1y", "5y"], horizontal=True, label_visibility="collapsed")

hist = yf.Ticker(chart_ticker).history(period=period)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist["Close"],
    mode="lines",
    name=chart_ticker,
    line=dict(color="#00c47a", width=1.5)
))

if not open_pos.empty:
    ticker_positions = open_pos[open_pos["ticker"] == chart_ticker]
    for _, pos in ticker_positions.iterrows():
        fig.add_trace(go.Scatter(
            x=[pos["buy_date"]],
            y=[pos["buy_price"]],
            mode="markers+text",
            marker=dict(color="#00c47a", size=10, symbol="triangle-up"),
            text=["ENTRY"],
            textposition="top center",
            textfont=dict(color="#00c47a", size=10),
            name=f"Entry @ {pos['buy_price']:.2f}"
        ))

if not closed.empty:
    ticker_closed = closed[closed["ticker"] == chart_ticker]
    for _, pos in ticker_closed.iterrows():
        fig.add_trace(go.Scatter(
            x=[pos["sell_date"]],
            y=[pos["sell_price"]],
            mode="markers+text",
            marker=dict(color="#e03e3e", size=10, symbol="triangle-down"),
            text=["EXIT"],
            textposition="bottom center",
            textfont=dict(color="#e03e3e", size=10),
            name=f"Exit @ {pos['sell_price']:.2f}"
        ))

fig.update_layout(
    paper_bgcolor="#0d0d0d",
    plot_bgcolor="#0d0d0d",
    font=dict(color="#666", size=11),
    xaxis=dict(gridcolor="#1a1a1a", showline=True, linecolor="#1a1a1a"),
    yaxis=dict(gridcolor="#1a1a1a", showline=True, linecolor="#1a1a1a"),
    legend=dict(bgcolor="#0d0d0d", bordercolor="#1a1a1a", borderwidth=1, font=dict(size=10)),
    margin=dict(l=40, r=20, t=20, b=40),
    height=420,
    title=dict(text=f"{chart_ticker}", font=dict(color="#e8e8e8", size=13), x=0)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(f"<p style='color:#333;font-size:10px;letter-spacing:1px;margin-top:32px;border-top:1px solid #1a1a1a;padding-top:16px'>ASR PLATFORM &nbsp;|&nbsp; NOT FINANCIAL ADVICE</p>", unsafe_allow_html=True)