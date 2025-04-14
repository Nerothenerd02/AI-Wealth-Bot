import requests
from bs4 import BeautifulSoup
import json

def get_yahoo_news():
    url = "https://finance.yahoo.com/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    headlines = [a.text.strip() for a in soup.find_all("h3") if a.text.strip()]
    return headlines[:5]

def get_google_news(query="stock market"):
    url = f"https://news.google.com/search?q={query}"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    articles = soup.find_all("a", class_="DY5T1d")
    return [a.text.strip() for a in articles[:5]]

def get_reddit_headlines():
    url = "https://www.reddit.com/r/CryptoCurrency/.json"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        posts = r.json()["data"]["children"]
        return [post["data"]["title"] for post in posts[:5]]
    return []

def get_finviz_news():
    url = "https://finviz.com/news.ashx"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.content, "html.parser")
    headlines = [a.text.strip() for a in soup.find_all("a", class_="nn-tab-link")]
    return headlines[:5]

def get_all_headlines():
    return (
        get_yahoo_news() +
        get_google_news() +
        get_reddit_headlines() +
        get_finviz_news()
    )

# Test the output
if __name__ == "__main__":
    all_headlines = get_all_headlines()
    print(json.dumps(all_headlines, indent=2))
