import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER
from datetime import datetime

def format_change(value):
    arrow = "▲" if value >= 0 else "▼"
    return f"{arrow} {abs(value):.2f}%"

def build_email_body(results):
    now = datetime.now().strftime("%A %d %B %Y")
    body = f"📈 DAILY STOCK REPORT — {now}\n\n"

    for r in results:
        body += f"{'='*55}\n"
        body += f"  {r['ticker']}  —  ${r['current_price']:.2f}\n"
        body += f"{'='*55}\n"
        body += f"  {'METRIC':<25} {'VALUE':>15}\n"
        body += f"  {'-'*40}\n"
        body += f"  {'24hr Change':<25} {format_change(r['change_1d']):>15}\n"
        body += f"  {'Weekly Change':<25} {format_change(r['change_1w']):>15}\n"
        body += f"  {'Monthly Change':<25} {format_change(r['change_1m']):>15}\n"
        body += f"  {'3 Month Change':<25} {format_change(r['change_3m']):>15}\n"
        body += f"  {'-'*40}\n"
        body += f"  {'52-Week High':<25} {'$'+str(round(r['52w_high'],2)):>15}\n"
        body += f"  {'52-Week Low':<25} {'$'+str(round(r['52w_low'],2)):>15}\n"
        body += f"{'='*55}\n\n"

    return body

def send_email(results):
    print("Building email...")
    body = build_email_body(results)
    print(body)

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(EMAIL_RECEIVER)
    msg["Subject"] = f"📈 Daily Stock Report"
    msg.attach(MIMEText(body, "plain"))

    print("Connecting to Gmail...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

    print("✅ Email sent successfully!")