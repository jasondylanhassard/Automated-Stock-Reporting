import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER
from datetime import datetime

def format_change(value):
    if value is None:
        return "<td style='color:gray;text-align:center'>N/A</td>"
    color = "#00c853" if value >= 0 else "#d50000"
    arrow = "▲" if value >= 0 else "▼"
    return f"<td style='color:{color};text-align:center'>{arrow} {abs(value):.2f}%</td>"

def format_price(value):
    if value is None or value == 0:
        return "<td style='text-align:center'>N/A</td>"
    return f"<td style='text-align:center'>${value:.2f}</td>"

def format_score(score):
    if score >= 66:
        color = "#00c853"
    elif score >= 36:
        color = "#ff9800"
    else:
        color = "#d50000"
    return f"<td style='text-align:center;font-weight:bold;color:{color}'>{score}/100</td>"

def format_verdict(verdict):
    if "BUY" in verdict:
        bg = "#00c853"
    elif "HOLD" in verdict:
        bg = "#ff9800"
    else:
        bg = "#d50000"
    return f"<td style='text-align:center;background-color:{bg};color:white;font-weight:bold;border-radius:4px;padding:6px 12px'>{verdict}</td>"

def build_email_body(results):
    now = datetime.now().strftime("%A %d %B %Y")

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <h2 style="color: #333;">📈 Daily Stock Report — {now}</h2>
        <table style="border-collapse: collapse; width: 100%; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <thead>
                <tr style="background-color: #1a1a2e; color: white;">
                    <th style="padding: 12px 16px; text-align:left">TICKER</th>
                    <th style="padding: 12px 16px; text-align:center">PRICE</th>
                    <th style="padding: 12px 16px; text-align:center">24HR</th>
                    <th style="padding: 12px 16px; text-align:center">1 WEEK</th>
                    <th style="padding: 12px 16px; text-align:center">1 MONTH</th>
                    <th style="padding: 12px 16px; text-align:center">3 MONTH</th>
                    <th style="padding: 12px 16px; text-align:center">52W HIGH</th>
                    <th style="padding: 12px 16px; text-align:center">52W LOW</th>
                    <th style="padding: 12px 16px; text-align:center">SCORE</th>
                    <th style="padding: 12px 16px; text-align:center">VERDICT</th>
                </tr>
            </thead>
            <tbody>
    """

    for i, r in enumerate(results):
        bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        html += f"""
            <tr style="background-color:{bg};">
                <td style="padding: 10px 16px; font-weight:bold;">{r['ticker']}</td>
                {format_price(r['current_price'])}
                {format_change(r['change_1d'])}
                {format_change(r['change_1w'])}
                {format_change(r['change_1m'])}
                {format_change(r['change_3m'])}
                {format_price(r['52w_high'])}
                {format_price(r['52w_low'])}
                {format_score(r.get('score', 0))}
                {format_verdict(r.get('verdict', '🟡 HOLD'))}
            </tr>
        """

    html += """
            </tbody>
        </table>
        <p style="color:#999;font-size:12px;margin-top:16px;">
            Score breakdown: 0-35 = SELL &nbsp;|&nbsp; 36-65 = HOLD &nbsp;|&nbsp; 66-100 = BUY
        </p>
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
    msg["Subject"] = "📈 Daily Stock Report"
    msg.attach(MIMEText(body, "html"))

    print("Connecting to Gmail...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

    print("✅ Email sent successfully!")