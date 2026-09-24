from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("TWELVE_API_KEY")

DATABASE = "sqlite:///data/market.db"

# Phase 1: fetch one base timeframe from Twelve Data and
# build higher timeframes locally to reduce API credit usage.
SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
]

BASE_TIMEFRAME = "1min"

TIMEFRAMES = [
    "1min",
    "5min",
    "15min",
    "1h",
    "4h",
]
