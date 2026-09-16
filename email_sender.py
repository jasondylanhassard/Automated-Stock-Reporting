import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER, DASHBOARD_URL
from datetime import datetime
from portfolio import get_open_positions, get_closed_positions, calculate_realised_pnl
import yfinance as yf

# ── COLOUR PALETTE ─────────────────────────────────────────
BG         = "#0d0d0d"
SURFACE    = "#141414"
SURFACE2   = "#1a1a1a"
BORDER     = "#2a2a2a"
GREEN      = "#00c47a"
RED        = "#e03e3e"
AMBER      = "#c47a00"
TEXT       = "#e8e8e8"
MUTED      = "#666666"
HEADER_BG  = "#0a1f0a"
HEADER_TXT = "#00c47a"

def format_change(value):
    if value is None:
        return f"<td style='color:{MUTED};text-align:center;padding:10px 14px'>—</td>"
    color = GREEN if value >= 0 else RED
    arrow = "+" if value >= 0 else ""
    return f"<td style='color:{color};text-align:center;padding:10px 14px;font-family:monospace'>{arrow}{value:.2f}%</td>"

def format_price(value):
    if value is None or value == 0:
        return f"<td style='color:{MUTED};text-align:center;padding:10px 14px'>—</td>"
    return f"<td style='color:{TEXT};text-align:center;padding:10px 14px;font-family:monospace'>{value:.2f}</td>"

def format_score(score):
    if score >= 66:
        color = GREEN
    elif score >= 36:
        color = AMBER
    else:
        color = RED
    return f"<td style='color:{color};text-align:center;padding:10px 14px;font-family:monospace;font-weight:600'>{score}</td>"

def format_verdict(verdict):
    if "BUY" in verdict:
        color = GREEN
        label = "BUY"
    elif "HOLD" in verdict:
        color = AMBER
        label = "HOLD"
    else:
        color = RED
        label = "SELL"
    return f"<td style='text-align:center;padding:10px 14px'><span style='color:{color};font-weight:700;font-size:12px;letter-spacing:1px;border:1px solid {color};padding:3px 10px;border-radius:2px'>{label}</span></td>"

def build_portfolio_section(results):
    price_map = {r["ticker"]: r["current_price"] for r in results}
    open_pos = get_open_positions()

    if open_pos.empty:
        return f"<p style='color:{MUTED};margin-top:30px;font-size:13px'>No open positions on record.</p>"

    html = f"""
    <h3 style="color:{HEADER_TXT};margin-top:48px;margin-bottom:16px;font-size:11px;letter-spacing:2px;text-transform:uppercase;font-family:Arial,sans-serif">Portfolio Positions</h3>
    <table style="border-collapse:collapse;width:100%;background:{SURFACE};border:1px solid {BORDER};">
        <thead>
            <tr style="background:{HEADER_BG};border-bottom:1px solid {GREEN};">
                <th style="padding:12px 14px;text-align:left;color:{HEADER_TXT};font-size:11px;letter-spacing:1px;font-family:Arial,sans-serif">TICKER</th>
                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px;font-family:Arial,sans-serif">ENTRY DATE</th>
                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px;font-family:Arial,sans-serif">ENTRY</th>
                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px;font-family:Arial,sans-serif">CURRENT</th>
                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px;font-family:Arial,sans-serif">QTY</th>
                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px;font-family:Arial,sans-serif">MKT VALUE</th>
                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px;font-family:Arial,sans-serif">P/L $</th>
                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px;font-family:Arial,sans-serif">P/L %</th>
            </tr>
        </thead>
        <tbody>
    """

    total_cost = 0
    total_value = 0

    for i, (_, row) in enumerate(open_pos.iterrows()):
        current = price_map.get(row["ticker"])
        if current is None:
            try:
                hist = yf.Ticker(row["ticker"]).history(period="5d")
                current = hist["Close"].iloc[-1] if len(hist) > 0 else row["buy_price"]
            except:
                current = row["buy_price"]

        pnl = (current - row["buy_price"]) * row["quantity"]
        pnl_pct = ((current - row["buy_price"]) / row["buy_price"]) * 100
        market_value = current * row["quantity"]
        cost = row["buy_price"] * row["quantity"]
        total_cost += cost
        total_value += market_value

        pnl_color = GREEN if pnl >= 0 else RED
        bg = SURFACE if i % 2 == 0 else SURFACE2

        html += f"""
        <tr style="background:{bg};border-bottom:1px solid {BORDER}">
            <td style="padding:10px 14px;color:{TEXT};font-weight:600;font-family:monospace;letter-spacing:1px">{row['ticker']}</td>
            <td style="padding:10px 14px;color:{MUTED};text-align:center;font-family:Arial,sans-serif;font-size:13px">{row['buy_date']}</td>
            <td style="padding:10px 14px;color:{TEXT};text-align:center;font-family:monospace">{row['buy_price']:.2f}</td>
            <td style="padding:10px 14px;color:{TEXT};text-align:center;font-family:monospace">{current:.2f}</td>
            <td style="padding:10px 14px;color:{MUTED};text-align:center;font-family:monospace">{row['quantity']:.0f}</td>
            <td style="padding:10px 14px;color:{TEXT};text-align:center;font-family:monospace">{market_value:.2f}</td>
            <td style="padding:10px 14px;color:{pnl_color};text-align:center;font-family:monospace;font-weight:600">{pnl:+.2f}</td>
            <td style="padding:10px 14px;color:{pnl_color};text-align:center;font-family:monospace;font-weight:600">{pnl_pct:+.2f}%</td>
        </tr>
        """

    total_pnl = total_value - total_cost
    total_pnl_pct = ((total_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0
    total_color = GREEN if total_pnl >= 0 else RED
    realised = calculate_realised_pnl()
    realised_color = GREEN if realised >= 0 else RED

    html += f"""
        </tbody>
        <tfoot>
            <tr style="background:{HEADER_BG};border-top:1px solid {GREEN}">
                <td colspan="5" style="padding:12px 14px;color:{HEADER_TXT};font-size:11px;letter-spacing:1px;font-family:Arial,sans-serif">TOTAL PORTFOLIO</td>
                <td style="padding:12px 14px;color:{TEXT};text-align:center;font-family:monospace;font-weight:600">{total_value:.2f}</td>
                <td style="padding:12px 14px;color:{total_color};text-align:center;font-family:monospace;font-weight:600">{total_pnl:+.2f}</td>
                <td style="padding:12px 14px;color:{total_color};text-align:center;font-family:monospace;font-weight:600">{total_pnl_pct:+.2f}%</td>
            </tr>
        </tfoot>
    </table>
    <p style="color:{MUTED};font-size:12px;margin-top:8px;font-family:Arial,sans-serif">
        Realised P/L (lifetime): <span style="color:{realised_color};font-family:monospace;font-weight:600">{realised:+,.2f}</span>
    </p>
    """

    return html

def build_email_body(results):
    now = datetime.now().strftime("%d %B %Y")
    time_now = datetime.now().strftime("%H:%M")

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;background-color:{BG};padding:32px;margin:0;">

        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:900px;margin:0 auto;">
            <tr>
                <td style="padding-bottom:24px;border-bottom:1px solid {GREEN};">
                    <span style="color:{GREEN};font-size:11px;letter-spacing:3px;font-weight:700">ASR PLATFORM</span>
                    <span style="color:{MUTED};font-size:11px;float:right;letter-spacing:1px">{now} &nbsp;|&nbsp; {time_now} AEST</span>
                </td>
            </tr>
            <tr>
                <td style="padding:24px 0 8px 0;">
                    <h1 style="color:{TEXT};font-size:22px;font-weight:600;margin:0;letter-spacing:1px">DAILY MARKET REPORT</h1>
                    <p style="color:{MUTED};font-size:12px;margin:4px 0 0 0;letter-spacing:1px">AUTOMATED INTELLIGENCE — EQUITY WATCHLIST</p>
                </td>
            </tr>
        </table>

        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:900px;margin:24px auto 0 auto;">
            <tr>
                <td>
                    <p style="color:{HEADER_TXT};font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px">Watchlist</p>
                    <table style="border-collapse:collapse;width:100%;background:{SURFACE};border:1px solid {BORDER};">
                        <thead>
                            <tr style="background:{HEADER_BG};border-bottom:1px solid {GREEN};">
                                <th style="padding:12px 14px;text-align:left;color:{HEADER_TXT};font-size:11px;letter-spacing:1px">TICKER</th>
                                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px">PRICE</th>
                                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px">24H</th>
                                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px">1W</th>
                                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px">1M</th>
                                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px">3M</th>
                                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px">52W H</th>
                                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px">52W L</th>
                                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px">SCORE</th>
                                <th style="padding:12px 14px;text-align:center;color:{HEADER_TXT};font-size:11px;letter-spacing:1px">SIGNAL</th>
                            </tr>
                        </thead>
                        <tbody>
    """

    for i, r in enumerate(results):
        bg = SURFACE if i % 2 == 0 else SURFACE2
        html += f"""
            <tr style="background:{bg};border-bottom:1px solid {BORDER};">
                <td style="padding:10px 14px;color:{TEXT};font-weight:600;font-family:monospace;letter-spacing:1px">{r['ticker']}</td>
                {format_price(r['current_price'])}
                {format_change(r['change_1d'])}
                {format_change(r['change_1w'])}
                {format_change(r['change_1m'])}
                {format_change(r['change_3m'])}
                {format_price(r['52w_high'])}
                {format_price(r['52w_low'])}
                {format_score(r.get('score', 0))}
                {format_verdict(r.get('verdict', 'HOLD'))}
            </tr>
        """

    html += f"""
                        </tbody>
                    </table>
                    <p style="color:{MUTED};font-size:11px;margin-top:8px;letter-spacing:1px;font-family:Arial,sans-serif">
                        SIGNAL BANDS &nbsp;|&nbsp; BUY: 66-100 &nbsp;|&nbsp; HOLD: 36-65 &nbsp;|&nbsp; SELL: 0-35
                    </p>
                </td>
            </tr>
        </table>

        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:900px;margin:0 auto;">
            <tr><td>{build_portfolio_section(results)}</td></tr>
        </table>

        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:900px;margin:32px auto 0 auto;">
            <tr>
                <td style="text-align:center;padding:24px 0;border-top:1px solid {BORDER};">
                    <a href="{DASHBOARD_URL}" style="color:{GREEN};text-decoration:none;font-size:11px;letter-spacing:2px;border:1px solid {GREEN};padding:10px 24px;font-family:Arial,sans-serif">
                        ACCESS PORTFOLIO DASHBOARD
                    </a>
                </td>
            </tr>
            <tr>
                <td style="text-align:center;padding-top:16px;">
                    <p style="color:{MUTED};font-size:10px;letter-spacing:1px;margin:0">ASR PLATFORM &nbsp;|&nbsp; AUTOMATED MARKET INTELLIGENCE &nbsp;|&nbsp; NOT FINANCIAL ADVICE</p>
                </td>
            </tr>
        </table>

    </body>
    </html>
    """

    return html

def send_email(results):
    print("Building email...")
    body = build_email_body(results)

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(EMAIL_RECEIVER)
    msg["Subject"] = f"Market Report — {datetime.now().strftime('%d %b %Y')}"
    msg.attach(MIMEText(body, "html"))

    print("Connecting to Gmail...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

    print("Email sent successfully!")