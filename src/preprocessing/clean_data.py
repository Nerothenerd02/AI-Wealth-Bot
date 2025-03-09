import pandas as pd
import re
import os

def clean_text(text):
    """
    Cleans text by removing URLs, special characters, and extra spaces.
    """
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)  # Remove URLs
    text = re.sub(r"[^A-Za-z0-9 ]+", "", text)  # Remove special characters
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
    return text.lower()

def preprocess_sentiment_data(file_path):
    """
    Reads sentiment data, cleans text, and saves processed data.
    
    Args:
        file_path (str): Path to CSV file containing raw sentiment data.
    
    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    try:
        df = pd.read_csv(file_path, encoding="utf-8")

        # Explicitly clean only the title column, keeping the score
        if "title" in df.columns:
            df["cleaned_text"] = df["title"].astype(str).apply(clean_text)
        else:
            raise ValueError("Column 'title' not found in dataset.")

        # Drop empty rows
        df.dropna(subset=["cleaned_text"], inplace=True)

        # Save cleaned data in "data/processed" directory
        processed_dir = "data/processed"
        os.makedirs(processed_dir, exist_ok=True)  # Ensure directory exists
        cleaned_path = os.path.join(processed_dir, "reddit_sentiment_cleaned.csv")

        df.to_csv(cleaned_path, index=False)
        print(f"✅ Processed data saved at {cleaned_path}")

        return df
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return None

# Example usage
if __name__ == "__main__":
    preprocess_sentiment_data("data/raw/reddit_sentiment.csv")
