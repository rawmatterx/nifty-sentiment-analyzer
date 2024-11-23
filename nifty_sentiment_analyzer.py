import streamlit as st
import yfinance as yf
import investpy
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Function to fetch Nifty 50 previous day close price
def get_nifty50_previous_close():
    ticker = '^NSEI'  # Nifty 50 index symbol
    data = yf.download(ticker, period='2d')
    if data.empty:
        st.error('Failed to fetch Nifty 50 data.')
        return None
    previous_close = data['Close'].iloc[-2]
    return previous_close

# Function to fetch DJIA previous day percentage move
def get_djia_previous_day_percentage_move():
    ticker = '^DJI'  # DJIA index symbol
    data = yf.download(ticker, period='2d')
    if data.empty:
        st.error('Failed to fetch DJIA data.')
        return None
    previous_close = data['Close'].iloc[-2]
    last_close = data['Close'].iloc[-1]
    percentage_move = ((last_close - previous_close) / previous_close) * 100
    return percentage_move

# Function to fetch real-time SGX Nifty price
def get_sgx_nifty_price():
    try:
        df = investpy.get_index_recent_data(index='SGX Nifty', country='india')
        current_price = df['Close'][-1]
        return current_price
    except Exception as e:
        st.error(f'Failed to fetch SGX Nifty data: {e}')
        return None

# Function to fetch historical data for Nifty 50
def get_nifty50_historical_data():
    ticker = '^NSEI'  # Nifty 50 index symbol
    data = yf.download(ticker, period='1mo')
    if data.empty:
        st.error('Failed to fetch Nifty 50 historical data.')
        return None
    return data

def main():
    st.title('Nifty Market Prediction App')

    # Step 1: Fetch SGX Nifty price at 8:45 AM today
    sgx_nifty_price = get_sgx_nifty_price()
    if sgx_nifty_price is None:
        st.stop()

    st.write(f"**SGX Nifty price at latest available time:** {sgx_nifty_price:.2f}")

    # Fetch Nifty 50 previous day's closing price
    previous_close_nifty = get_nifty50_previous_close()
    if previous_close_nifty is None:
        st.stop()

    st.write(f"**Nifty 50 previous close price:** {previous_close_nifty:.2f}")

    # Calculate the difference
    difference = sgx_nifty_price - previous_close_nifty

    # Determine how Nifty will open
    if -40 <= difference <= 40:
        opening = 'Flat'
    elif difference > 100:
        opening = 'Huge Gap Up'
    elif difference > 40:
        opening = 'Gap Up'
    elif difference < -100:
        opening = 'Huge Gap Down'
    elif difference < -40:
        opening = 'Gap Down'
    else:
        opening = 'Flat'

    st.write(f"**Difference between SGX Nifty and Nifty 50 previous close:** {difference:.2f}")
    st.write(f"**Nifty is expected to open:** {opening}")

    # Step 2: Fetch DJIA previous day percentage move
    djia_percentage_move = get_djia_previous_day_percentage_move()
    if djia_percentage_move is None:
        st.stop()

    # Determine market sentiment
    sentiment = 'Positive' if djia_percentage_move > 0 else 'Negative'
    st.write(f"**DJIA moved:** {djia_percentage_move:.2f}% yesterday.")
    st.write(f"**Market sentiment is expected to be:** {sentiment}")

    # Step 3: Convert DJIA percentage move into Nifty 50 price movement
    close_point = (djia_percentage_move / 100) * previous_close_nifty
    st.write(f"**Expected Nifty 50 movement based on DJIA:** {close_point:.2f} points")

    # Step 4: Determine market trend
    open_point = difference
    if abs(close_point) > 2 * abs(open_point):
        if close_point > 0:
            market_trend = 'Bullish Move'
        else:
            market_trend = 'Bearish Move'
    else:
        market_trend = 'Volatile/Sideways'

    st.write(f"**Based on calculations, the market is expected to have a:** {market_trend}")

    # Historical Analysis
    st.header('Historical Analysis')

    nifty_data = get_nifty50_historical_data()
    if nifty_data is not None:
        st.subheader('Nifty 50 Closing Prices - Last Month')
        fig = px.line(nifty_data, x=nifty_data.index, y='Close', title='Nifty 50 Closing Prices')
        st.plotly_chart(fig)

        # Moving Averages
        nifty_data['MA20'] = nifty_data['Close'].rolling(window=20).mean()
        nifty_data['MA50'] = nifty_data['Close'].rolling(window=50).mean()

        st.subheader('Nifty 50 with Moving Averages')
        fig_ma = px.line(nifty_data, x=nifty_data.index, y=['Close', 'MA20', 'MA50'], title='Nifty 50 with Moving Averages')
        st.plotly_chart(fig_ma)

        # Show data table
        st.subheader('Nifty 50 Historical Data')
        st.dataframe(nifty_data.tail(10))

    else:
        st.write('Historical data not available.')

if __name__ == "__main__":
    main()


