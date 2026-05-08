from data_fetcher import fetch_all_stocks
from email_sender import send_email
from scoring import calculate_score

results = fetch_all_stocks()

for stock in results:
    hist = stock.pop("hist")
    score_data = calculate_score(stock, hist)
    stock["score"] = score_data["score"]
    stock["verdict"] = score_data["verdict"]
    stock["breakdown"] = score_data["breakdown"]

send_email(results)