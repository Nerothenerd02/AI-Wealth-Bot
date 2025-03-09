import praw
import os
import pandas as pd
from dotenv import load_dotenv

# Load API credentials
load_dotenv()

# Load API credentials from environment variables
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="AI-Wealth-Sentiment"
)

def fetch_reddit_sentiment(subreddit="cryptocurrency", limit=100, save_csv=True):
    """
    Scrapes recent Reddit posts for sentiment analysis.

    Args:
        subreddit (str): The subreddit to scrape (e.g., 'cryptocurrency')
        limit (int): Number of posts to fetch
        save_csv (bool): Whether to save the data as a CSV file.

    Returns:
        pd.DataFrame: DataFrame containing post titles and scores.
    """
    try:
        print(f"📡 Fetching Reddit sentiment data from r/{subreddit} (Limit: {limit})...")

        posts = []
        for post in reddit.subreddit(subreddit).hot(limit=limit):
            posts.append([post.title, post.score])

        df = pd.DataFrame(posts, columns=["title", "score"])

        print(f"✅ Successfully fetched {len(df)} posts from r/{subreddit}.")

        # Save to CSV in the correct path
        if save_csv:
            output_dir = "data/raw"
            os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
            file_path = os.path.join(output_dir, "reddit_sentiment.csv")
            df.to_csv(file_path, index=False)
            print(f"📂 Data saved to {file_path}")

        return df

    except Exception as e:
        print(f"❌ Error fetching Reddit sentiment data: {e}")
        return None

# Example usage
if __name__ == "__main__":
    df = fetch_reddit_sentiment()
    if df is not None:
        print("\n📊 Sample Reddit Sentiment Data:")
        print(df.head())
