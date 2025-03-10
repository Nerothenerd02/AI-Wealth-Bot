import pandas as pd
import os
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from src.preprocessing.clean_text import clean_text  # Import the cleaning function

# Initialize VADER Sentiment Analyzer
vader_analyzer = SentimentIntensityAnalyzer()

class SentimentAnalysis:
    """
    A class responsible for analyzing sentiment of scraped text.
    """

    @staticmethod
    def analyze_vader(text):
        """
        Analyzes sentiment using VADER.
        Returns:
            Compound Score (-1 to 1): Negative (-1), Neutral (0), Positive (1)
        """
        return vader_analyzer.polarity_scores(text)["compound"]

    @staticmethod
    def analyze_textblob(text):
        """
        Analyzes sentiment using TextBlob.
        Returns:
            Polarity (-1 to 1): Negative (-1), Neutral (0), Positive (1)
        """
        return TextBlob(text).sentiment.polarity

    @staticmethod
    def process_sentiment(file_path):
        """
        Reads Reddit sentiment data, cleans text, and applies sentiment analysis.

        Args:
            file_path (str): Path to CSV file containing raw Reddit data.

        Returns:
            pd.DataFrame: Cleaned and processed DataFrame.
        """
        try:
            df = pd.read_csv(file_path, encoding="utf-8")

            if "title" not in df.columns:
                raise ValueError("Column 'title' not found in dataset.")

            # ✅ Clean the text using `clean_text.py`
            df["cleaned_text"] = df["title"].astype(str).apply(clean_text)

            # ✅ Apply sentiment analysis
            df["vader_sentiment"] = df["cleaned_text"].apply(SentimentAnalysis.analyze_vader)
            df["textblob_sentiment"] = df["cleaned_text"].apply(SentimentAnalysis.analyze_textblob)

            # ✅ Save processed sentiment data in "data/processed"
            processed_dir = "data/processed"
            os.makedirs(processed_dir, exist_ok=True)  # Ensure directory exists
            cleaned_path = os.path.join(processed_dir, "reddit_sentiment_analyzed.csv")

            df.to_csv(cleaned_path, index=False)
            print(f"✅ Sentiment analysis saved at {cleaned_path}")

            return df
        except Exception as e:
            print(f"❌ Error processing sentiment: {e}")
            return None

# Example usage
if __name__ == "__main__":
    SentimentAnalysis.process_sentiment("data/raw/reddit_sentiment.csv")
