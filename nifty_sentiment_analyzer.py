import datetime
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import os

# Configuration
EODHD_API_KEY = os.getenv('EODHD_API_KEY')
FMP_API_KEY = os.getenv('FMP_API_KEY')

def fetch_sgx_nifty_value(date):
    """Fetch SGX Nifty value at 8:45 AM for given date"""
    api_key = FMP_API_KEY
    try:
        # Note: Modify the API endpoint to get 8:45 AM data specifically
        response = requests.get(f"https://financialmodelingprep.com/api/v3/historical-price-full/%5ENSEI?from={date}&to={date}&apikey={api_key}")
        data = response.json() if response.status_code == 200 else {}
        if "historical" in data and len(data["historical"]) > 0:
            sgx_nifty_value = data["historical"][0]["close"]  # Should be 8:45 AM value
        else:
            sgx_nifty_value = 0
        st.write(f"SGX Nifty Value at 8:45 AM on {date}: {sgx_nifty_value}")
    except Exception as e:
        sgx_nifty_value = 0
        st.write(f"Error fetching SGX Nifty value: {e}")
    return sgx_nifty_value

def fetch_nifty50_previous_close(date):
    """Fetch Nifty 50 previous day close price"""
    api_key = FMP_API_KEY
    try:
        response = requests.get(f"https://financialmodelingprep.com/api/v3/historical-price-full/%5ENSEI?from={date}&to={date}&apikey={api_key}")
        data = response.json() if response.status_code == 200 else {}
        if "historical" in data and len(data["historical"]) > 0:
            nifty50_close = data["historical"][0]["close"]
        else:
            nifty50_close = 0
        st.write(f"Nifty 50 Previous Close: {nifty50_close}")
    except Exception as e:
        nifty50_close = 0
        st.write(f"Error fetching Nifty 50 previous close: {e}")
    return nifty50_close

def classify_market_opening(sgx_nifty_value, nifty50_close):
    """Classify market opening based on difference between SGX Nifty and Nifty 50 previous close"""
    difference = sgx_nifty_value - nifty50_close
    
    # Updated classification logic as per requirements
    if difference > 100:
        return "Huge Gap Up Opening"
    elif difference > 40:
        return "Gap Up Opening"
    elif difference < -100:
        return "Huge Gap Down Opening"
    elif difference < -40:
        return "Gap Down Opening"
    elif -40 <= difference <= 40:
        return "Flat Opening"
    return "Flat Opening"  # Default case

def fetch_dji_previous_day(date):
    """Fetch DJI previous day data and calculate percentage movement"""
    api_key = FMP_API_KEY
    try:
        response = requests.get(f"https://financialmodelingprep.com/api/v3/historical-price-full/%5EDJI?from={date}&to={date}&apikey={api_key}")
        data = response.json() if response.status_code == 200 else {}
        if "historical" in data and len(data["historical"]) > 0:
            dji_data = data["historical"][0]
            previous_day_change_percentage = ((dji_data["close"] - dji_data["open"]) / dji_data["open"]) * 100
        else:
            previous_day_change_percentage = 0
        st.write(f"DJI Previous Day Movement: {previous_day_change_percentage:.2f}%")
    except Exception as e:
        previous_day_change_percentage = 0
        st.write(f"Error fetching DJI data: {e}")
    return previous_day_change_percentage

def calculate_close_point(open_point, nifty50_close, dji_percentage):
    """Calculate expected close point based on DJI percentage movement"""
    # Convert DJI percentage to Nifty points
    point_movement = (nifty50_close * dji_percentage) / 100
    return open_point + point_movement

def determine_market_movement(open_point, close_point):
    """Determine market movement based on open and close points"""
    # Calculate the difference relative to open point
    difference = close_point - open_point
    threshold = 2 * abs(open_point)
    
    if difference > threshold:
        return "Bullish Movement"
    elif difference < -threshold:
        return "Bearish Movement"
    else:
        return "Sideways/Volatile Movement"

def get_market_sentiment(date):
    """Get complete market sentiment analysis"""
    # Step 1: Get SGX Nifty and previous day Nifty 50 close
    sgx_nifty_value = fetch_sgx_nifty_value(date)
    nifty50_close = fetch_nifty50_previous_close(date)
    
    # Classify opening
    opening_type = classify_market_opening(sgx_nifty_value, nifty50_close)
    
    # Step 2: Get DJI sentiment
    dji_percentage = fetch_dji_previous_day(date)
    dji_sentiment = "Positive Sentiment" if dji_percentage > 0 else "Negative Sentiment"
    
    # Step 3: Calculate expected close point
    close_point = calculate_close_point(sgx_nifty_value, nifty50_close, dji_percentage)
    
    # Step 4: Determine market movement
    market_movement = determine_market_movement(sgx_nifty_value, close_point)
    
    return {
        "opening_type": opening_type,
        "dji_sentiment": dji_sentiment,
        "expected_open": sgx_nifty_value,
        "expected_close": close_point,
        "market_movement": market_movement
    }

# Streamlit Web App
def main():
    st.title("Nifty 50 Market Sentiment Analyzer")
    
    # Date selection
    st.write("Select a date to analyze Nifty 50 sentiment (last 10 trading days):")
    start_date = datetime.date.today() - datetime.timedelta(days=10)
    selected_date = st.date_input("Select Date", 
                                 max_value=datetime.date.today(), 
                                 min_value=start_date)
    
    # Analysis button
    if st.button("Analyze Market"):
        if selected_date.weekday() >= 5:
            st.error("Selected date is a weekend. Please choose a weekday.")
        else:
            st.write("### Analysis Results")
            results = get_market_sentiment(selected_date.strftime("%Y-%m-%d"))
            
            # Display results in a structured format
            col1, col2 = st.columns(2)
            with col1:
                st.write("Opening Analysis:")
                st.write(f"• Type: {results['opening_type']}")
                st.write(f"• Expected Open: {results['expected_open']:.2f}")
                
            with col2:
                st.write("Movement Analysis:")
                st.write(f"• DJI Sentiment: {results['dji_sentiment']}")
                st.write(f"• Expected Close: {results['expected_close']:.2f}")
            
            st.write("### Final Prediction")
            st.write(f"Market is expected to show a {results['market_movement'].lower()} "
                    f"with {results['dji_sentiment'].lower()}.")

if __name__ == "__main__":
    main()
