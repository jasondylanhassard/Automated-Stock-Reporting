import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER

def build_email_body(results):
    body = "📈 DAILY STOCK REPORT\n"
    body += "=" * 45 + "\n\n"

    for r in results:
        body += f"{'='*45}\n"
        body += f"  {r['ticker']}  —  ${r['current_price']:.2f}\n"
        body += f"{'='*45}\n"
        body += f"  52-Week High:  ${r['52w_high']:.2f}\n"
        body += f"  52-Week Low:   ${r['52w_low']:.2f}\n"
        body += f"  P/E Ratio:     {r['pe_ratio']}\n"
        body += f"  MA50:          ${r['ma_short']}\n"
        body += f"  MA200:         ${r['ma_long']}\n"
        body += "\n"

    return body

def send_email(results):
    print("Building email...")
    body = build_email_body(results)

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