import os
from src.data_collection.yahoo_finance import fetch_yahoo_data
from src.data_collection.binance_api import fetch_binance_data
from src.data_collection.sentiment_scrapper import RedditScraper
from src.preprocessing.sentiment_analysis import SentimentAnalysis  # ✅ Corrected import

# Ensure necessary directories exist
os.makedirs("data/raw", exist_ok=True)  # Ensure raw data directory exists

# 📈 Step 1: Collect financial data
print("Fetching Yahoo Finance data...")
yahoo_df = fetch_yahoo_data("BTC-USD")
if yahoo_df is not None:
    yahoo_df.to_csv("data/raw/yahoo_btc.csv", index=False)  # Save in 'data/raw'

print("Fetching Binance data...")
binance_df = fetch_binance_data()
if binance_df is not None:
    binance_df.to_csv("data/raw/binance_btc.csv", index=False)  # Save in 'data/raw'

# 📰 Step 2: Fetch Reddit Sentiment Data (Raw)
print("Fetching Reddit sentiment data...")
scraper = RedditScraper(subreddit="cryptocurrency", limit=100)
reddit_df = scraper.fetch_data()
reddit_df.to_csv("data/raw/reddit_sentiment.csv", index=False)  # Save in 'data/raw'

# 🧹 Step 3: Process Sentiment Data (Cleaning + Sentiment Analysis)
print("Cleaning and analyzing Reddit sentiment data...")
SentimentAnalysis.process_sentiment("data/raw/reddit_sentiment.csv")  # ✅ Calls sentiment processing

print("✅ Data pipeline completed successfully!")
