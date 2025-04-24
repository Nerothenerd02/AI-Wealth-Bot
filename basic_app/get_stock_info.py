import yfinance as yf
import time

def getStockInfo(ticker_symbol, retries=3, delay=1):
    for _ in range(retries):
        try:
            ticker_symbol = ticker_symbol.strip().upper()
            stock = yf.Ticker(ticker_symbol)
            info = stock.info

            # Fallback: if info is empty or missing expected fields
            if not info or 'symbol' not in info:
                raise ValueError("Invalid or empty response from yfinance")

            return {
                'symbol': info.get('symbol', ticker_symbol),
                'name': info.get('shortName', 'Unavailable'),
                'exchange': info.get('exchange', 'Unavailable'),
                'price': info.get('currentPrice', 'N/A'),
                'sector': info.get('sector', 'Unknown'),
            }
        except Exception as e:
            print(f"[Retrying] Failed to fetch {ticker_symbol} - {e}")
            time.sleep(delay)

    # Final fallback after all retries
    return {
        'symbol': ticker_symbol,
        'name': 'Data not available',
        'exchange': 'N/A',
        'price': 'N/A',
        'sector': 'N/A'
    }
