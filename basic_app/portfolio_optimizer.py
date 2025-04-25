import yfinance as yf
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import json
import matplotlib.pyplot as plt
import argparse
import sys
import os

# Dynamically locate the static folder relative to the script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Current script directory
STATIC_DIR = os.path.join(BASE_DIR, "..", "..", "static")  # Adjust path to locate 'static'
OUTPUT_DIR = os.path.join(STATIC_DIR, "dashboard_outputs", "Markowitz_Results")

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def fetch_data(tickers, start, end):
    try:
        data = yf.download(tickers, start=start, end=end, auto_adjust=False)
        data = data["Adj Close"]
        if data.empty:
            raise ValueError("No data fetched. Check ticker symbols or date range.")
        return data.dropna()
    except Exception as e:
        print(f"Error fetching data from yfinance: {e}")
        sys.exit(1)

def portfolio_performance(weights, mean_returns, cov_matrix):
    returns = np.dot(weights, mean_returns)
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return -returns / std

def optimize_portfolio(data):
    mean_returns = data.pct_change().mean()
    cov_matrix = data.pct_change().cov()
    num_assets = len(data.columns)
    bounds = tuple((0, 1) for _ in range(num_assets))
    init_guess = [1. / num_assets] * num_assets
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}

    result = minimize(portfolio_performance, init_guess,
                      args=(mean_returns, cov_matrix),
                      method='SLSQP', bounds=bounds, constraints=constraints)
    if not result.success:
        raise ValueError("Optimization failed.")
    return dict(zip(data.columns, result.x))

def plot_allocation(weights, save_path):
    labels = list(weights.keys())
    sizes = list(weights.values())

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
    ax.axis('equal')
    plt.title("Optimal Portfolio Allocation")
    plt.savefig(save_path)
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize Portfolio Allocation using Markowitz Model")
    parser.add_argument("--tickers", type=str, default="BTC-USD,ETH-USD,SOL-USD,SPY",
                        help="Comma-separated ticker symbols.")
    parser.add_argument("--start_date", type=str, default="2023-01-01", help="Start date.")
    parser.add_argument("--end_date", type=str, default="2024-01-01", help="End date.")

    args = parser.parse_args()

    try:
        tickers = args.tickers.split(",")
        price_data = fetch_data(tickers, args.start_date, args.end_date)
        weights = optimize_portfolio(price_data)

        weights_path = os.path.join(OUTPUT_DIR, "markowitz_weights.json")
        chart_path = os.path.join(OUTPUT_DIR, "optimal_allocation.png")

        with open(weights_path, "w") as f:
            json.dump({k: round(v, 4) for k, v in weights.items()}, f, indent=2)

        plot_allocation(weights, save_path=chart_path)

        print("✅ Optimization complete.")
        print(f"📁 Weights → {weights_path}")
        print(f"📊 Chart   → {chart_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
