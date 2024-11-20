import datetime
import requests
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to fetch NSE holidays using EODHD API
def fetch_nse_holidays():
    api_key = os.getenv('EODHD_API_KEY')  # Ensure your API key is stored securely
    url = f"https://eodhd.com/api/exchange-details/NSE?api_token={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            holidays = data.get('Holidays', [])
            holiday_dates = [datetime.datetime.strptime(holiday['date'], '%Y-%m-%d').date() for holiday in holidays]
            return holiday_dates
        else:
            st.error("Failed to fetch NSE holidays.")
            return []
    except Exception as e:
        st.error(f"Error fetching NSE holidays: {e}")
        return []

# Function to fetch SGX Nifty value at 8:45 am
def fetch_sgx_nifty_value():
    api_key = os.getenv('FMP_API_KEY')
    try:
        response = requests.get(f"https://financialmodelingprep.com/api/v3/quote/%5ENSEI?apikey={api_key}")
        if response.status_code == 200:
            sgx_nifty_change = response.json()[0]["change"]
        else:
            sgx_nifty_change = 0  # Default value in case of an error
    except Exception as e:
        sgx_nifty_change = 0  # Handle exception and set a default value
    return sgx_nifty_change

# Function to fetch SPX 500 data for the previous day
def fetch_spx500_previous_day():
    api_key = os.getenv('FMP_API_KEY')
    try:
        response = requests.get(f"https://financialmodelingprep.com/api/v3/historical-price-full/^GSPC?timeseries=2&apikey={api_key}")
        if response.status_code == 200:
            spx_data = response.json()["historical"]
            spx_data_yesterday = spx_data[1]
            spx_data_dict = {"close": spx_data_yesterday["close"], "open": spx_data_yesterday["open"]}
        else:
            spx_data_dict = {"close": 0, "open": 0}  # Default value in case of an error
    except Exception as e:
        spx_data_dict = {"close": 0, "open": 0}  # Handle exception and set a default value
    return spx_data_dict

# Function to classify the market opening sentiment
def classify_market_opening(sgx_nifty_change):
    if sgx_nifty_change > 100:
        return "Huge Gap Up Opening"
    elif sgx_nifty_change > 40:
        return "Gap Up Opening"
    elif sgx_nifty_change < -100:
        return "Huge Gap Down Opening"
    elif sgx_nifty_change < -40:
        return "Gap Down Opening"
    elif -40 <= sgx_nifty_change <= 40:
        return "Flat Opening"
    else:
        return "Flat Neutral Opening"

# Function to get SPX 500 sentiment
def get_spx500_sentiment(spx_data):
    if spx_data["close"] > spx_data["open"]:
        return "Positive Sentiment"
    elif spx_data["close"] < spx_data["open"]:
        return "Negative Sentiment"
    else:
        return "Neutral Sentiment"

# Function to predict Nifty movement based on SGX Nifty and SPX 500
def predict_nifty_movement(sgx_nifty_change, spx_sentiment):
    if sgx_nifty_change > 0 and spx_sentiment == "Positive Sentiment":
        return "Bullish Movement"
    elif sgx_nifty_change < 0 and spx_sentiment == "Negative Sentiment":
        return "Bearish Movement"
    else:
        return "Sideways Movement"

# Function to check if today is a trading day
def is_trading_day():
    nse_holidays = fetch_nse_holidays()
    today = datetime.date.today()
    if today in nse_holidays or today.weekday() >= 5:  # If today is a holiday or weekend
        return False
    return True

# Function to get the market sentiment at 8:45 am
def get_market_sentiment():
    sgx_nifty_change = fetch_sgx_nifty_value()
    spx_data = fetch_spx500_previous_day()
    spx_sentiment = get_spx500_sentiment(spx_data)
    market_opening_sentiment = classify_market_opening(sgx_nifty_change)
    if sgx_nifty_change > 0:
        nifty_slope = "Positive"
    elif sgx_nifty_change < 0:
        nifty_slope = "Negative"
    else:
        nifty_slope = "Flat"

    if nifty_slope == "Positive":
        nifty_prediction = "Bullish Movement"
    elif nifty_slope == "Negative":
        nifty_prediction = "Bearish Movement"
    else:
        nifty_prediction = "Sideways/Volatile Movement"

    return market_opening_sentiment, nifty_prediction, spx_sentiment

# Streamlit Web App
st.title("Nifty 50 Sentiment Analyzer")

# Check market status based on time
current_time = datetime.datetime.now()
if not is_trading_day():
    st.write("Non-Trading Day: The NSE market is closed today.")
elif current_time.hour > 15 or (current_time.hour == 15 and current_time.minute > 30):
    st.write("Market Closed: The market has closed for today.")
elif current_time.hour >= 9 and current_time.minute >= 15:
    st.write("Market Is Already Open: Please analyze before market opens.")
else:
    if st.button("Analyze Today's Nifty 50"):
        sentiment = get_market_sentiment()
        if isinstance(sentiment, tuple):
            market_opening_sentiment, nifty_prediction, spx_sentiment = sentiment
            st.write(f"Today I am expecting a {market_opening_sentiment} in the market after which a {nifty_prediction} with {spx_sentiment.lower()}.")
        else:
            st.write(sentiment)


