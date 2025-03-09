from binance.client import Client
import pandas as pd
import os

# Load Binance API keys from environment variables
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Initialize Binance client
client = Client(API_KEY, API_SECRET)

def calculate_rsi(data, window=14):
    """
    Calculates the Relative Strength Index (RSI) and ensures the first `window` days are NaN.

    Args:
        data (pd.DataFrame): Dataframe containing price data.
        window (int): Number of periods for RSI calculation.

    Returns:
        pd.Series: RSI values with NaN for the first `window` days.
    """
    delta = data["close"].astype(float).diff(1)  # Price changes
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Ensure first `window` values are NaN
    rsi.iloc[:window] = None  

    return rsi.clip(0, 100)

def fetch_binance_data(symbol="BTCUSDT", interval="1d", limit=500, save_csv=True):
    """
    Fetch historical crypto data from Binance API, calculate technical indicators, and save as CSV.

    Args:
        symbol (str): Trading pair (e.g., 'BTCUSDT')
        interval (str): Time interval (e.g., '1m', '1h', '1d')
        limit (int): Number of historical data points to retrieve
        save_csv (bool): Whether to save the data as a CSV file.

    Returns:
        pd.DataFrame: DataFrame with historical data and technical indicators.
    """
    try:
        print(f"📡 Fetching Binance data for {symbol} (Interval: {interval}, Limit: {limit})...")

        # Fetch historical OHLCV data
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)

        # Convert to DataFrame
        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_vol", "trades", "taker_buy_base_vol",
            "taker_buy_quote_vol", "ignore"
        ])

        # Convert timestamp to datetime format
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        # Convert prices & volume to float
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)

        # Keep only necessary columns
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]

        print(f"✅ Successfully fetched {len(df)} records for {symbol}.")

        # 📌 Compute technical indicators
        df["SMA_50"] = df["close"].rolling(window=50, min_periods=1).mean()
        df["SMA_200"] = df["close"].rolling(window=200, min_periods=1).mean()
        df["RSI"] = calculate_rsi(df)

        # Save data to CSV in the same directory as Yahoo data
        if save_csv:
            output_dir = "data/raw"
            os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
            file_path = os.path.join(output_dir, f"{symbol}_historical.csv")
            df.to_csv(file_path, index=False)
            print(f"📂 Data saved to {file_path}")

        return df

    except Exception as e:
        print(f"❌ Error fetching Binance data for {symbol}: {e}")
        return None

# Example usage
if __name__ == "__main__":
    df = fetch_binance_data()
    if df is not None:
        print("\n📊 Sample Binance Data with Technical Indicators:")
        print(df.head())
