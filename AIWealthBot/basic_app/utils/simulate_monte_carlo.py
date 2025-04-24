import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import base64
import argparse
import json
import sys
import os
from io import BytesIO

# Dynamically locate the 'static' folder relative to script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "..", "..", "static")
OUTPUT_DIR = os.path.join(STATIC_DIR, "dashboard_outputs", "MonteCarlo_Results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_returns(tickers, start, end):
    try:
        data = yf.download(tickers, start=start, end=end, auto_adjust=False)
        data = data["Adj Close"] if isinstance(data.columns, pd.MultiIndex) else data
        data = data.dropna()
        returns = data.pct_change().dropna()
        return returns.mean(axis=1)
    except Exception as e:
        print(f"Error fetching data from yfinance: {e}")
        sys.exit(1)

def simulate_monte_carlo(start_value, days, simulations, mu, sigma):
    if start_value <= 0 or days <= 0 or simulations <= 0:
        raise ValueError("start_value, days, and simulations must be positive numbers.")

    daily_returns = np.random.normal(mu, sigma, (simulations, days))
    return start_value * np.cumprod(1 + daily_returns, axis=1)

def plot_simulation(data, save_path):
    plt.figure(figsize=(10, 6))
    for i in range(min(100, data.shape[0])):
        plt.plot(data[i], color='blue', alpha=0.05)

    plt.plot(data.mean(axis=0), color='red', label='Mean Portfolio Value')
    plt.title("Monte Carlo Simulation of Portfolio Growth")
    plt.xlabel("Days")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()

    with open(save_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monte Carlo Simulation for Portfolio Growth")
    parser.add_argument("--tickers", type=str, default="BTC-USD,ETH-USD,SOL-USD,SPY")
    parser.add_argument("--start_date", type=str, default="2023-01-01")
    parser.add_argument("--end_date", type=str, default="2024-01-01")
    parser.add_argument("--start_value", type=float, default=10000)
    parser.add_argument("--days", type=int, default=365)
    parser.add_argument("--simulations", type=int, default=1000)

    args = parser.parse_args()

    try:
        tickers = args.tickers.split(",")
        portfolio_returns = fetch_returns(tickers, args.start_date, args.end_date)
        mu = portfolio_returns.mean()
        sigma = portfolio_returns.std()

        sim_data = simulate_monte_carlo(
            start_value=args.start_value,
            days=args.days,
            simulations=args.simulations,
            mu=mu,
            sigma=sigma
        )

        # Save outputs
        chart_path = os.path.join(OUTPUT_DIR, "monte_carlo_projection.png")
        txt_path = os.path.join(OUTPUT_DIR, "monte_carlo_projection.txt")

        base64_chart = plot_simulation(sim_data, save_path=chart_path)

        with open(txt_path, "w") as f:
            f.write(base64_chart)

        print("✅ Monte Carlo simulation complete.")
        print(f"📊 Chart: {chart_path}")
        print(f"📦 Base64 text: {txt_path}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
