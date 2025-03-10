import praw
import os
import pandas as pd
from dotenv import load_dotenv

# Load API credentials
load_dotenv()

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="AI-Wealth-Sentiment"
)

class RedditScraper:
    """
    A class responsible for scraping Reddit data.
    """

    def __init__(self, subreddit="cryptocurrency", limit=100):
        self.subreddit = subreddit
        self.limit = limit

    def fetch_data(self):
        """
        Fetches Reddit posts without sentiment analysis.

        Returns:
            pd.DataFrame: DataFrame containing raw Reddit data.
        """
        print(f"📡 Fetching Reddit data from r/{self.subreddit} (Limit: {self.limit})...")

        posts = []
        for post in reddit.subreddit(self.subreddit).hot(limit=self.limit):
            posts.append([post.title, post.score])

        df = pd.DataFrame(posts, columns=["title", "score"])
        print(f"✅ Successfully fetched {len(df)} posts.")

        return df

# Example usage
if __name__ == "__main__":
    scraper = RedditScraper()
    df = scraper.fetch_data()
    print(df.head())
