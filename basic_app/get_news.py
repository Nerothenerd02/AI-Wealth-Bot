import requests
import random
from django.templatetags.static import static
from basic_app.sentiment_analysis import predict_sentiment

NEWS_API_KEY = "9b23adeb6a634a0ba1f62e76dcbc54de"
PAGE_SIZE    = 12
PLACEHOLDER  = static('images/news_placeholder.png')


def getNews(key):
    """
    Fetch up to PAGE_SIZE news articles about `key` (string).
    Returns a list of dicts with title, description, author, url, image.
    No sentiment analysis.
    """
    try:
        url = (
            f"https://newsapi.org/v2/everything"
            f"?q={requests.utils.quote(key)}"
            f"&pageSize={PAGE_SIZE}"
            f"&apiKey={NEWS_API_KEY}"
        )
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[getNews] Network error: {e}")
        return []

    news_list = []
    if data.get('status') == 'ok' and 'articles' in data:
        articles = data['articles']
        sampled = random.sample(articles, min(PAGE_SIZE, len(articles)))
        for article in sampled:
            title       = article.get('title') or "No title available"
            description = article.get('description') or "No description available"
            author      = article.get('author') or "Unknown author"
            link        = article.get('url') or "#"
            img         = article.get('urlToImage') or ""
            if not img.startswith('http'):
                img = PLACEHOLDER

            news_list.append({
                'title':       title,
                'description': description,
                'author':      author,
                'url':         link,
                'image':       img,
            })
    else:
        print("[getNews] No valid articles found.")

    return news_list


def getNewsWithSentiment(stock_name):
    """
    Same as getNews(), but also runs sentiment analysis
    on each article’s combined title+description.
    """
    try:
        url = (
            f"https://newsapi.org/v2/everything"
            f"?q={requests.utils.quote(stock_name)}"
            f"&pageSize={PAGE_SIZE}"
            f"&apiKey={NEWS_API_KEY}"
        )
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[getNewsWithSentiment] Network error: {e}")
        return []

    news_list = []
    if data.get('status') == 'ok' and 'articles' in data:
        articles = data['articles']
        sampled = random.sample(articles, min(PAGE_SIZE, len(articles)))

        # build texts for batch sentiment
        texts = []
        for art in sampled:
            txt = (art.get('title') or "") + ". " + (art.get('description') or "")
            texts.append(txt.strip() or "No content available")

        sentiments = predict_sentiment(texts)

        for art, sentiment in zip(sampled, sentiments):
            title       = art.get('title') or "No title available"
            description = art.get('description') or "No description available"
            author      = art.get('author') or "Unknown author"
            link        = art.get('url') or "#"
            img         = art.get('urlToImage') or ""
            if not img.startswith('http'):
                img = PLACEHOLDER
                print(f"[IMAGE] ⚠️ No valid image, using placeholder.")
            else:
                print(f"[IMAGE] ✅ Using external image: {img}")

            news_list.append({
                'title':       title,
                'description': description,
                'author':      author,
                'url':         link,
                'image':       img,
                'sentiment':   sentiment,
            })
    else:
        print("[getNewsWithSentiment] No valid articles found.")

    return news_list
