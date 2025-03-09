import yfinance as yf
import pandas as pd
import os

def calculate_rsi(data, window=14):
    """
    Calculates the Relative Strength Index (RSI) and ensures the first `window` days are NaN.

    Args:
        data (pd.DataFrame): Dataframe containing stock price data.
        window (int): Number of periods for RSI calculation.

    Returns:
        pd.Series: RSI values with NaN for the first `window` days.
    """
    delta = data["Close"].diff(1)  # Price changes
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Ensure first `window` values are NaN
    rsi.iloc[:window] = None  

    return rsi.clip(0, 100)

def fetch_yahoo_data(ticker, start_date="2023-01-01", end_date="2024-01-01", save_csv=True):
    """
    Fetches historical stock/crypto data from Yahoo Finance, including OHLCV and technical indicators.

    Args:
        ticker (str): Stock or crypto ticker (e.g., 'AAPL', 'BTC-USD').
        start_date (str): Start date for historical data (YYYY-MM-DD).
        end_date (str): End date for historical data (YYYY-MM-DD).
        save_csv (bool): Whether to save the data as a CSV file.

    Returns:
        pd.DataFrame: DataFrame containing historical data and technical indicators.
    """
    try:
        print(f"📡 Fetching data for {ticker} from {start_date} to {end_date}...")

        # Fetch OHLCV data
        data = yf.download(ticker, start=start_date, end=end_date)

        # Check if data is empty (Invalid Ticker or API issue)
        if data.empty:
            print(f"⚠️ Warning: No data found for {ticker}. Check if the ticker is correct.")
            return None

        print(f"✅ Successfully fetched {len(data)} records for {ticker}.")

        # Compute technical indicators
        data["SMA_50"] = data["Close"].rolling(window=50, min_periods=1).mean()  # 50-day SMA
        data["SMA_200"] = data["Close"].rolling(window=200, min_periods=1).mean()  # 200-day SMA
        data["RSI"] = calculate_rsi(data)  # Fixed RSI calculation

        # Save data as CSV
        if save_csv:
            output_dir = "data/raw"
            os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
            file_path = os.path.join(output_dir, f"{ticker}_historical.csv")
            data.to_csv(file_path, index=False)
            print(f"📂 Data for {ticker} saved to {file_path}")

        return data  # Return a DataFrame instead of a dictionary

    except Exception as e:
        print(f"❌ Error fetching data for {ticker}: {e}")
        return None

# Example usage
if __name__ == "__main__":
    ticker = "BTC-USD"
    df = fetch_yahoo_data(ticker)

    if df is not None:
        print("\n📊 Sample Data:")
        print(df.head())
