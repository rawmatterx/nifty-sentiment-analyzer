import datetime
from fmp_python.fmp import FMP
import streamlit as st
import streamlit.components.v1 as components

# Initialize the FMP client with your API key
api_key = 'vptSViEFdGn6TJrvmWAkFx2MMaJBxvOJ'
fmp = FMP(api_key=api_key, output_format='pandas')

# Function to fetch Nifty 50 end-of-day value
def fetch_nifty50_value(date):
    try:
        historical_data = fmp.get_historical_price('^NSEI', _from=date, _to=date)
        if not historical_data.empty:
            nifty50_close = historical_data.iloc[0]['close']
        else:
            nifty50_close = 0  # No data available for the given date
        st.write(f"Nifty 50 Data on {date}: {historical_data}")  # Debug statement
    except Exception as e:
        nifty50_close = 0  # Handle exception and set a default value
        st.write(f"Error fetching Nifty 50 value: {e}")  # Log the exception
    return nifty50_close

# Function to fetch Dow Jones Industrial Average (DJI) previous day end-of-day close price and calculate percentage movement
def fetch_dji_previous_day(date):
    try:
        historical_data = fmp.get_historical_price('^DJI', _from=date, _to=date)
        if not historical_data.empty:
            dji_data = historical_data.iloc[0]
            previous_day_change_percentage = ((dji_data['close'] - dji_data['open']) / dji_data['open']) * 100
        else:
            previous_day_change_percentage = 0  # No data available for the given date
        st.write(f"DJI Data on {date}: {historical_data}")  # Debug statement
    except Exception as e:
        previous_day_change_percentage = 0  # Handle exception and set a default value
        st.write(f"Error fetching DJI data: {e}")  # Log the exception
    return previous_day_change_percentage

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

# Function to get the market sentiment for a specific date
def get_market_sentiment(date):
    nifty50_close = fetch_nifty50_value(date)
    sgx_nifty_value = fetch_nifty50_value(date)  # Assuming SGX Nifty data is similar to Nifty 50 for this example
    market_opening_sentiment = classify_market_opening(nifty50_close, sgx_nifty_value)
    dji_change_percentage = fetch_dji_previous_day(date)
    dji_sentiment = get_dji_sentiment(dji_change_percentage)
    close_point = calculate_close_point(nifty50_close, dji_change_percentage)
    st.write(f"Calculated Close Point on {date}: {close_point}")  # Debug statement
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

# Date selection for analysis
st.write("Select a date to analyze Nifty 50 sentiment (last 10 trading days):")
start_date = datetime.date.today() - datetime.timedelta(days=10)
selected_date = st.date_input("Select Date", max_value=datetime.date.today(), min_value=start_date)

# Button to analyze the market sentiment for the selected date
if st.button("Analyze Nifty 50 for Selected Date"):
    if selected_date.weekday() >= 5:
        st.write("Non-Trading Day: The market is closed on weekends.")
    else:
        sentiment = get_market_sentiment(selected_date.strftime("%Y-%m-%d"))
        if isinstance(sentiment, tuple):
            market_opening_sentiment, market_movement, dji_sentiment = sentiment
            st.write(f"For {selected_date}, I am expecting a {market_opening_sentiment} in the market after which a {market_movement} with {dji_sentiment.lower()}.")
        else:
            st.write(sentiment)

