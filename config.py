from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("TWELVE_API_KEY")

DATABASE = "sqlite:///data/market.db"

SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT"
]

TIMEFRAMES = [
    "1min",
    "5min",
    "15min",
    "1h",
    "4h"
]