import re

def clean_text(text):
    """
    Cleans text by removing URLs, special characters, and extra spaces.
    """
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)  # Remove URLs
    text = re.sub(r"[^A-Za-z0-9 ]+", "", text)  # Remove special characters
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
    return text.lower()
