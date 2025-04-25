import os
import csv
import json
import random
import numpy as np
from datetime import datetime, timedelta

# Setup output directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "..", "..", "static")
OUTPUT_DIR = os.path.join(STATIC_DIR, "dashboard_outputs", "TradeLog_Results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configuration
ASSETS = ["BTC", "ETH", "SOL"]
START_CASH = 10000
DAYS = 30

def simulate_trades():
    portfolio = {asset: 0 for asset in ASSETS}
    cash = START_CASH
    log = []

    for day in range(DAYS):
        date = (datetime.now() - timedelta(days=(DAYS - day))).strftime("%Y-%m-%d")
        for asset in ASSETS:
            price = round(np.random.uniform(80, 300), 2)
            action = random.choice(["BUY", "SELL", "HOLD"])

            if action == "BUY" and cash >= price:
                qty = round(cash * 0.1 / price, 4)
                portfolio[asset] += qty
                cash -= qty * price
            elif action == "SELL" and portfolio[asset] > 0:
                qty = round(portfolio[asset] * 0.25, 4)
                portfolio[asset] -= qty
                cash += qty * price
            else:
                qty = 0.0  # HOLD

            log.append({
                "date": date,
                "asset": asset,
                "action": action,
                "price": price,
                "quantity": round(qty, 4),
                "remaining_cash": round(cash, 2)
            })

    return log

def save_trade_log(log):
    # CSV
    csv_path = os.path.join(OUTPUT_DIR, "trade_log.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=log[0].keys())
        writer.writeheader()
        writer.writerows(log)

    # JSON
    json_path = os.path.join(OUTPUT_DIR, "trade_log.json")
    with open(json_path, "w") as f:
        json.dump(log, f, indent=2)

    print("✅ Trade log saved:")
    print(f"📁 CSV → {csv_path}")
    print(f"📁 JSON → {json_path}")

if __name__ == "__main__":
    trade_log = simulate_trades()
    save_trade_log(trade_log)
