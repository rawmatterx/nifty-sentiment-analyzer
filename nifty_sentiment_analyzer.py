import datetime
import requests
import pandas as pd
import streamlit as st

# Function to fetch SGX Nifty value at 8:45 am
def fetch_sgx_nifty_value():
    try:
        response = requests.get(f"https://financialmodelingprep.com/api/v3/quote/%5ENSEI?apikey={st.secrets['API_KEY']}")
        if response.status_code == 200:
            sgx_nifty_change = response.json()[0]["change"]
        else:
            sgx_nifty_change = 0  # Default value in case of an error
    except Exception as e:
        sgx_nifty_change = 0  # Handle exception and set a default value
    return sgx_nifty_change

# Function to fetch SPX 500 data for the previous day
def fetch_spx500_previous_day():
    try:
        response = requests.get(f"https://financialmodelingprep.com/api/v3/historical-price-full/^GSPC?timeseries=2&apikey={st.secrets['API_KEY']}")
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
    if sgx_nifty_change > 40 and spx_sentiment == "Positive Sentiment":
        return "Bullish Movement"
    elif sgx_nifty_change < -40 and spx_sentiment == "Negative Sentiment":
        return "Bearish Movement"
    else:
        return "Sideways Movement"

# Function to get the market sentiment at 8:45 am
def get_market_sentiment():
    sgx_nifty_change = fetch_sgx_nifty_value()
    spx_data = fetch_spx500_previous_day()
    spx_sentiment = get_spx500_sentiment(spx_data)
    market_opening_sentiment = classify_market_opening(sgx_nifty_change)
    nifty_prediction = predict_nifty_movement(sgx_nifty_change, spx_sentiment)
    return market_opening_sentiment, nifty_prediction

# Streamlit Web App
st.title("Nifty 50 Sentiment Analyzer")

if st.button("Analyze Today's Nifty 50"):
    sentiment = get_market_sentiment()
    if isinstance(sentiment, tuple):
        market_opening_sentiment, nifty_prediction = sentiment
        st.write(f"Market Opening Sentiment: {market_opening_sentiment}")
        st.write(f"Predicted Nifty Movement: {nifty_prediction}")
    else:
        st.write(sentiment)
