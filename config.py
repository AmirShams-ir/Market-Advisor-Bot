from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("TWELVE_API_KEY")
DATA_DIR = "data"
DEFAULT_EXCHANGE = "Binance"
DEFAULT_TIMEFRAMES = ["1h", "4h", "1day", "1week"]
FETCH_OUTPUTSIZE = 500
