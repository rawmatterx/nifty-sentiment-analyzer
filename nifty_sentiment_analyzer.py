import datetime
import streamlit as st
import streamlit.components.v1 as components

# Function to classify the market opening sentiment based on Nifty 50 previous close and SGX Nifty value
def classify_market_opening(nifty50_close, sgx_nifty_value):
    difference = sgx_nifty_value - nifty50_close
    if -40 <= difference <= 40:
        return "Flat Opening"
    elif difference > 100:
        return "Huge Gap Up Opening"
    elif difference > 40:
        return "Gap Up Opening"
    elif difference < -100:
        return "Huge Gap Down Opening"
    elif difference < -40:
        return "Gap Down Opening"
    else:
        return "Flat Neutral Opening"

# Function to get DJI sentiment
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

# Function to get the market sentiment based on user input
def get_market_sentiment(nifty50_close, sgx_nifty_value, dji_change_percentage):
    market_opening_sentiment = classify_market_opening(nifty50_close, sgx_nifty_value)
    dji_sentiment = get_dji_sentiment(dji_change_percentage)
    close_point = calculate_close_point(nifty50_close, dji_change_percentage)
    market_movement = determine_market_movement(sgx_nifty_value, close_point)
    return market_opening_sentiment, market_movement, dji_sentiment

# Streamlit Web App
st.title("Nifty 50 Sentiment Analyzer - Web Calculator")

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

# User input for analysis
st.write("Enter the required data points to analyze Nifty 50 sentiment:")
nifty50_close = st.number_input("Enter Nifty 50 Previous Close Value:", min_value=0.0, step=0.01)
sgx_nifty_value = st.number_input("Enter SGX Nifty Value at 8:45 AM:", min_value=0.0, step=0.01)
dji_change_percentage = st.number_input("Enter Dow Jones Industrial Average (DJI) Previous Day Change Percentage:", step=0.01)

# Button to analyze the market sentiment based on user input
if st.button("Analyze Nifty 50 Sentiment"):
    sentiment = get_market_sentiment(nifty50_close, sgx_nifty_value, dji_change_percentage)
    if isinstance(sentiment, tuple):
        market_opening_sentiment, market_movement, dji_sentiment = sentiment
        st.write(f"Based on the provided data, I am expecting a {market_opening_sentiment} in the market after which a {market_movement} with {dji_sentiment.lower()}.")
    else:
        st.write(sentiment)



