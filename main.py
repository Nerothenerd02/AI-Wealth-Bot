import os
from src.data_collection.yahoo_finance import fetch_yahoo_data
from src.data_collection.binance_api import fetch_binance_data
from src.data_collection.sentiment_scrapper import fetch_reddit_sentiment
from src.preprocessing.clean_data import preprocess_sentiment_data

# Ensure necessary directories exist
os.makedirs("data/raw", exist_ok=True)  # Ensure raw data directory exists

# 📈 Collect financial data
print("Fetching Yahoo Finance data...")
yahoo_df = fetch_yahoo_data("BTC-USD")
if yahoo_df is not None:
    yahoo_df.to_csv("data/raw/yahoo_btc.csv", index=False)  # Save in 'data/raw'

print("Fetching Binance data...")
binance_df = fetch_binance_data()
if binance_df is not None:
    binance_df.to_csv("data/raw/binance_btc.csv", index=False)  # Save in 'data/raw'

# 📰 Collect Reddit sentiment data
print("Fetching Reddit sentiment data...")
reddit_df = fetch_reddit_sentiment(subreddit="cryptocurrency")
if reddit_df is not None:
    reddit_df.to_csv("data/raw/reddit_sentiment.csv", index=False)  # Save in 'data/raw'

# 🧹 Preprocess Reddit sentiment data
print("Cleaning Reddit sentiment data...")
preprocess_sentiment_data("data/raw/reddit_sentiment.csv")  # Process in 'data/raw'

print("✅ Data pipeline completed successfully!")
