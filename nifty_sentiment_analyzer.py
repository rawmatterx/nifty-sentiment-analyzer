import datetime
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import os

# Load environment variables from .env file manually
EODHD_API_KEY = os.getenv('EODHD_API_KEY')
FMP_API_KEY = os.getenv('FMP_API_KEY')

# Function to fetch SGX Nifty value at 8:45 am
def fetch_sgx_nifty_value():
    api_key = FMP_API_KEY
    try:
        response = requests.get(f"https://financialmodelingprep.com/api/v3/quote/%5ENSEI?apikey={api_key}")
        if response.status_code == 200:
            sgx_nifty_value = response.json()[0]["price"]
        else:
            sgx_nifty_value = 0  # Default value in case of an error
    except Exception as e:
        sgx_nifty_value = 0  # Handle exception and set a default value
    return sgx_nifty_value

# Function to fetch Nifty 50 previous day close price
def fetch_nifty50_previous_close():
    api_key = FMP_API_KEY
    try:
        response = requests.get(f"https://financialmodelingprep.com/api/v3/quote/%5ENSEI?apikey={api_key}")
        if response.status_code == 200:
            nifty50_close = response.json()[0]["previousClose"]
        else:
            nifty50_close = 0  # Default value in case of an error
    except Exception as e:
        nifty50_close = 0  # Handle exception and set a default value
    return nifty50_close

# Function to classify the market opening sentiment based on SGX Nifty and Nifty 50 previous close
def classify_market_opening(sgx_nifty_value, nifty50_close):
    difference = sgx_nifty_value - nifty50_close
    if -40 <= difference <= 40:
        return "Flat Opening"
    elif difference > 100:
        return "Huge Gap Up Opening"
    elif difference > 40:
        return "Gap Up Opening"
    elif difference > -100:
        return "Huge Gap Down Opening"
    elif difference > -40:
        return "Gap Down Opening"
    else:
        return "Flat Neutral Opening"

# Function to fetch Dow Jones Industrial Average (DJI) previous day close price and calculate percentage movement
def fetch_dji_previous_day():
    api_key = FMP_API_KEY
    try:
        response = requests.get(f"https://financialmodelingprep.com/api/v3/historical-price-full/^DJI?timeseries=2&apikey={api_key}")
        if response.status_code == 200:
            dji_data = response.json()["historical"][0]
            previous_day_change_percentage = ((dji_data["close"] - dji_data["open"]) / dji_data["open"]) * 100
            return previous_day_change_percentage
        else:
            return 0  # Default value in case of an error
    except Exception as e:
        return 0  # Handle exception and set a default value

# Function to get SPX 500 sentiment
def get_dji_sentiment(change_percentage):
    if change_percentage > 0:
        return "Positive Sentiment"
    elif change_percentage < 0:
        return "Negative Sentiment"
    else:
        return "Neutral Sentiment"

# Function to calculate the close point based on DJI movement percentage and Nifty 50 previous day close
def calculate_close_point(nifty50_close, change_percentage):
    return nifty50_close * (1 + (change_percentage / 100))

# Function to determine market movement based on open and close points
def determine_market_movement(open_point, close_point):
    difference = close_point - open_point
    if difference > 2 * open_point:
        return "Bullish Movement"
    elif difference < -2 * open_point:
        return "Bearish Movement"
    else:
        return "Sideways/Volatile Movement"

# Function to get the market sentiment at 8:45 am
def get_market_sentiment():
    sgx_nifty_value = fetch_sgx_nifty_value()
    nifty50_close = fetch_nifty50_previous_close()
    market_opening_sentiment = classify_market_opening(sgx_nifty_value, nifty50_close)
    dji_change_percentage = fetch_dji_previous_day()
    dji_sentiment = get_dji_sentiment(dji_change_percentage)
    close_point = calculate_close_point(nifty50_close, dji_change_percentage)
    market_movement = determine_market_movement(sgx_nifty_value, close_point)
    return market_opening_sentiment, market_movement, dji_sentiment

# Streamlit Web App
st.title("Nifty 50 Sentiment Analyzer")

# Add Microsoft Clarity tracking code
components.html(
    """
    <script type="text/javascript">
        (function(c,l,a,r,i,t,y){
            c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
            t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
            y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
        })(window, document, "clarity", "script", "p1n8m63pzi");
    </script>
    """,
    height=0  # Set height to 0 to make the script invisible
)

# Button to analyze the market sentiment
if st.button("Analyze Today's Nifty 50"):
    current_time = datetime.datetime.now()
    if current_time.weekday() >= 5:
        st.write("Non-Trading Day: The market is closed on weekends.")
    elif current_time.hour > 15 or (current_time.hour == 15 and current_time.minute > 30):
        st.write("Market Closed: The market has closed for today.")
    elif current_time.hour >= 9 and current_time.minute >= 15:
        st.write("Market Is Already Open: Please analyze before market opens.")
    else:
        sentiment = get_market_sentiment()
        if isinstance(sentiment, tuple):
            market_opening_sentiment, market_movement, dji_sentiment = sentiment
            st.write(f"Today I am expecting a {market_opening_sentiment} in the market after which a {market_movement} with {dji_sentiment.lower()}.")
        else:
            st.write(sentiment)


