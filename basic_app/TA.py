import pandas as pd
import yfinance as yf
import ta

def sma(ticker):
    df = yf.Ticker(ticker).history(period='1y').reset_index()
    df['SMA'] = ta.trend.sma_indicator(df['Close'], window=20)
    return df[['Date', 'SMA']].dropna()

def ema(ticker):
    df = yf.Ticker(ticker).history(period='1y').reset_index()
    df['EMA'] = ta.trend.ema_indicator(df['Close'], window=20)
    return df[['Date', 'EMA']].dropna()

def macd(ticker):
    df = yf.Ticker(ticker).history(period='1y').reset_index()
    df['MACD'] = ta.trend.macd(df['Close'])
    df['MACD_SIGNAL'] = ta.trend.macd_signal(df['Close'])
    return df[['Date', 'MACD', 'MACD_SIGNAL']].dropna()

def rsi(ticker):
    df = yf.Ticker(ticker).history(period='1y').reset_index()
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    return df[['Date', 'RSI']].dropna()

def obv(ticker):
    df = yf.Ticker(ticker).history(period='1y').reset_index()
    df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])
    return df[['Date', 'OBV']].dropna()

def bband(ticker):
    df = yf.Ticker(ticker).history(period='1y').reset_index()
    bb = ta.volatility.BollingerBands(df['Close'], window=20)
    df['BB_UPPER'] = bb.bollinger_hband()
    df['BB_LOWER'] = bb.bollinger_lband()
    df['BB_MID'] = bb.bollinger_mavg()
    return df[['Date', 'BB_UPPER', 'BB_LOWER', 'BB_MID']].dropna()

def pivots(ticker):
    df = yf.Ticker(ticker).history(interval='1d').tail(1).reset_index()
    pp = (df['High'] + df['Low'] + df['Close']) / 3
    r1 = 2 * pp - df['Low']
    s1 = 2 * pp - df['High']
    r2 = pp + (df['High'] - df['Low'])
    s2 = pp - (df['High'] - df['Low'])
    r3 = pp + 2 * (df['High'] - df['Low'])
    s3 = pp - 2 * (df['High'] - df['Low'])
    return float(pp), float(r1), float(r2), float(r3), float(s1), float(s2), float(s3)
