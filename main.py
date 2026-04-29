from data_fetcher import fetch_all_stocks
from email_sender import send_email

results = fetch_all_stocks()
send_email(results)