import urllib.request
import json
import time
from django.core.cache import cache
from urllib.error import HTTPError, URLError

def getStockInfo(var):
    var = var.strip().replace(' ', '')
    cache_key = f"stockinfo_{var}"
    
    # Try to return from cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    url = f"https://finance.yahoo.com/_finance_doubledown/api/resource/searchassist;searchTerm={var}?device=console&returnMeta=true"

    try:
        # Rate limit buffer
        time.sleep(1)

        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())

        # Cache response for 5 minutes
        items = data.get('data', {}).get('items', [])
        cache.set(cache_key, items, timeout=300)
        return items

    except HTTPError as e:
        if e.code == 429:
            print(f"[Rate Limit] Yahoo API: Too many requests for '{var}'")
        else:
            print(f"[HTTPError] Code: {e.code}, URL: {url}")
        return []

    except URLError as e:
        print(f"[URLError] Failed to reach the server: {e.reason}")
        return []

    except Exception as e:
        print(f"[Unexpected Error] {e}")
        return []
