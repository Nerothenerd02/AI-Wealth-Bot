import tweepy
import os
import pandas as pd
from dotenv import load_dotenv

# Load API credentials
load_dotenv()

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(os.getenv("TWITTER_API_KEY"), os.getenv("TWITTER_API_SECRET"))
auth.set_access_token(os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_SECRET"))
api = tweepy.API(auth, wait_on_rate_limit=True)

def fetch_twitter_sentiment(query="cryptocurrency", limit=100, save_csv=True):
    """
    Scrapes recent tweets for sentiment analysis.

    Args:
        query (str): Search query (e.g., 'cryptocurrency')
        limit (int): Number of tweets to fetch
        save_csv (bool): Whether to save the data as a CSV file.

    Returns:
        pd.DataFrame: DataFrame containing tweet text and favorite counts.
    """
    try:
        print(f"📡 Fetching Twitter sentiment data for query: '{query}' (Limit: {limit})...")

        tweets = []
        for tweet in tweepy.Cursor(api.search_tweets, q=query, lang="en", tweet_mode="extended").items(limit):
            tweets.append([tweet.full_text, tweet.favorite_count])

        df = pd.DataFrame(tweets, columns=["tweet", "favorites"])

        print(f"✅ Successfully fetched {len(df)} tweets related to '{query}'.")

        # Save to CSV
        if save_csv:
            output_dir = "data/raw"
            os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
            file_path = os.path.join(output_dir, "twitter_sentiment.csv")
            df.to_csv(file_path, index=False)
            print(f"📂 Data saved to {file_path}")

        return df

    except Exception as e:
        print(f"❌ Error fetching Twitter sentiment data: {e}")
        return None

# Example usage
if __name__ == "__main__":
    df = fetch_twitter_sentiment()
    if df is not None:
        print("\n📊 Sample Twitter Sentiment Data:")
        print(df.head())
