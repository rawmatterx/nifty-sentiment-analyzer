# 1. API Key Management
# Instead of direct environment variable access, implement a config class:
class Config:
    def __init__(self):
        self.EODHD_API_KEY = os.getenv('EODHD_API_KEY')
        self.FMP_API_KEY = os.getenv('FMP_API_KEY')
        
        if not self.FMP_API_KEY:
            raise ValueError("FMP_API_KEY environment variable is not set")

# 2. API Integration
# Create a dedicated API client class:
class MarketDataClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"
        
    def get_historical_price(self, symbol, date):
        url = f"{self.base_url}/historical-price-full/{symbol}"
        params = {
            "from": date,
            "to": date,
            "apikey": self.api_key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for non-200 status codes
        return response.json()

# 3. Data Caching
# Implement caching to prevent redundant API calls:
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_market_data(symbol, date):
    client = MarketDataClient(Config().FMP_API_KEY)
    return client.get_historical_price(symbol, date)

# 4. Input Validation
def validate_date(date):
    if isinstance(date, str):
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
    
    if date.weekday() >= 5:
        raise ValueError("Selected date is a weekend")

# 5. Constants and Configuration
MARKET_THRESHOLDS = {
    "HUGE_GAP": 100,
    "GAP": 40,
    "FLAT_RANGE": (-40, 40)
}

# 6. Enhanced Market Classification
def classify_market_opening(sgx_nifty_value, nifty50_close):
    difference = sgx_nifty_value - nifty50_close
    
    if MARKET_THRESHOLDS["FLAT_RANGE"][0] <= difference <= MARKET_THRESHOLDS["FLAT_RANGE"][1]:
        return "Flat Opening"
    elif difference > MARKET_THRESHOLDS["HUGE_GAP"]:
        return "Huge Gap Up Opening"
    elif difference > MARKET_THRESHOLDS["GAP"]:
        return "Gap Up Opening"
    elif difference < -MARKET_THRESHOLDS["HUGE_GAP"]:
        return "Huge Gap Down Opening"
    elif difference < -MARKET_THRESHOLDS["GAP"]:
        return "Gap Down Opening"
    else:
        return "Flat Neutral Opening"

# 7. Improved Error Handling
class MarketDataError(Exception):
    """Custom exception for market data related errors"""
    pass

def safe_api_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            raise MarketDataError(f"API request failed: {str(e)}")
        except ValueError as e:
            raise MarketDataError(f"Invalid data: {str(e)}")
        except Exception as e:
            raise MarketDataError(f"Unexpected error: {str(e)}")
    return wrapper

# 8. Session State Management
def initialize_session_state():
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = []

# 9. Results Storage
def store_analysis_result(date, sentiment_data):
    if 'analysis_results' in st.session_state:
        st.session_state.analysis_results.append({
            'date': date,
            'sentiment': sentiment_data
        })

# 10. UI Improvements
def display_analysis_results():
    if st.session_state.analysis_results:
        for result in st.session_state.analysis_results:
            with st.expander(f"Analysis for {result['date']}"):
                st.json(result['sentiment'])
                
# Usage in main app:
def main():
    initialize_session_state()
    st.title("Nifty 50 Sentiment Analyzer")
    
    try:
        config = Config()
        client = MarketDataClient(config.FMP_API_KEY)
        
        selected_date = st.date_input(
            "Select Date",
            max_value=datetime.date.today(),
            min_value=datetime.date.today() - datetime.timedelta(days=10)
        )
        
        if st.button("Analyze Nifty 50"):
            validate_date(selected_date)
            sentiment = get_market_sentiment(selected_date.strftime("%Y-%m-%d"))
            store_analysis_result(selected_date, sentiment)
            display_analysis_results()
            
    except MarketDataError as e:
        st.error(f"Analysis failed: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
