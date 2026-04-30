import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER
from datetime import datetime

def format_change(value):
    if value is None:
        return "N/A"
    arrow = "▲" if value >= 0 else "▼"
    return f"{arrow} {abs(value):.2f}%"

def format_price(value):
    if value is None or value == 0:
        return "N/A"
    return f"${value:.2f}"

def build_email_body(results):
    now = datetime.now().strftime("%A %d %B %Y")
    body = f"📈 DAILY STOCK REPORT — {now}\n\n"

    # Column headers
    col_ticker  = 10
    col_price   = 10
    col_1d      = 10
    col_1w      = 10
    col_1m      = 10
    col_3m      = 10
    col_52h     = 12
    col_52l     = 12

    header = (
        f"{'TICKER':<{col_ticker}}"
        f"{'PRICE':>{col_price}}"
        f"{'24HR':>{col_1d}}"
        f"{'1 WEEK':>{col_1w}}"
        f"{'1 MONTH':>{col_1m}}"
        f"{'3 MONTH':>{col_3m}}"
        f"{'52W HIGH':>{col_52h}}"
        f"{'52W LOW':>{col_52l}}"
    )

    divider = "-" * len(header)

    body += divider + "\n"
    body += header + "\n"
    body += divider + "\n"

    for r in results:
        row = (
            f"{r['ticker']:<{col_ticker}}"
            f"{format_price(r['current_price']):>{col_price}}"
            f"{format_change(r['change_1d']):>{col_1d}}"
            f"{format_change(r['change_1w']):>{col_1w}}"
            f"{format_change(r['change_1m']):>{col_1m}}"
            f"{format_change(r['change_3m']):>{col_3m}}"
            f"{format_price(r['52w_high']):>{col_52h}}"
            f"{format_price(r['52w_low']):>{col_52l}}"
        )
        body += row + "\n"

    body += divider + "\n"
    return body

def send_email(results):
    print("Building email...")
    body = build_email_body(results)
    print(body)

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(EMAIL_RECEIVER)
    msg["Subject"] = "📈 Daily Stock Report"
    msg.attach(MIMEText(body, "plain"))

    print("Connecting to Gmail...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

    print("✅ Email sent successfully!")