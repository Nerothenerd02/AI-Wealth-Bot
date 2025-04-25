from prophet import Prophet
import yfinance as yf 
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def forecast(ticker):
    df = yf.Ticker(ticker).history(period='5y', interval='1d')
    df = df[['Close']].reset_index()

    # Prophet needs 'ds' and 'y' columns
    dfx = pd.DataFrame()
    dfx['ds'] = pd.to_datetime(df['Date']).dt.tz_localize(None)  # remove timezone
    dfx['y'] = df['Close'].values

    fbp = Prophet(daily_seasonality=True)
    fbp.fit(dfx)

    fut = fbp.make_future_dataframe(periods=365)
    forecast_df = fbp.predict(fut)

    # Plot and save to buffer
    fig = fbp.plot(forecast_df)
    buf = BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')

    # Calculate trend-based rating
    pchange = ((forecast_df.trend.values[-1] - dfx.y.values[-1]) * 100) / dfx.y.values[-1]
    if pchange > 0:
        rating = 1
    elif pchange == 0:
        rating = 0
    else:
        rating = -1

    return image_base64  # Only returning the image now
