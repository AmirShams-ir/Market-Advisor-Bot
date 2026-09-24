from __future__ import annotations

from typing import Dict

import pandas as pd
from twelvedata import TDClient

from config import API_KEY, FETCH_OUTPUTSIZE, SYMBOLS, TIMEFRAMES
from core.database import engine

td = TDClient(apikey=API_KEY)

# Twelve Data intervals map to pandas resampling rules.
RESAMPLE_RULES: Dict[str, str] = {}


def fetch_timeframe(symbol: str, timeframe: str) -> pd.DataFrame:
    """Fetch the base timeframe once for a symbol."""
    ts = td.time_series(
        symbol=symbol,
        exchange=__import__("config").EXCHANGE,
        interval=timeframe,
        outputsize=FETCH_OUTPUTSIZE,
        timezone="UTC",
    )
    df = ts.as_pandas().reset_index()

    if df.empty:
        return df

    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    for column in ("open", "high", "low", "close"):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Volume is optional in Twelve Data responses for some instruments/markets.
    # Keep the OHLC series usable even when volume is absent.
    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    else:
        df["volume"] = 0.0

    return df.dropna(subset=["datetime", "open", "high", "low", "close"])


def resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Kept for compatibility; timeframes are now fetched directly from Twelve Data."""
    result = df.copy()
    result["symbol"] = df["symbol"].iloc[0]
    result["timeframe"] = timeframe

    columns = [
        "symbol",
        "timeframe",
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    return result[columns]


def save_candles(df: pd.DataFrame) -> None:
    """Persist candles, replacing an existing identical key."""
    if df.empty:
        return

    # SQLite primary key prevents duplicates, so write one row at a time
    # with INSERT OR REPLACE for deterministic incremental updates.
    rows = df.to_dict(orient="records")

    with engine.begin() as conn:
        for row in rows:
            conn.exec_driver_sql(
                """
                INSERT OR REPLACE INTO candles
                (symbol, timeframe, datetime, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["symbol"],
                    row["timeframe"],
                    row["datetime"].isoformat(),
                    float(row["open"]),
                    float(row["high"]),
                    float(row["low"]),
                    float(row["close"]),
                    float(row["volume"]) if pd.notna(row["volume"]) else None,
                ),
            )


def update_symbol(symbol: str) -> None:
    """Fetch all configured timeframes directly from Twelve Data."""
    for timeframe in TIMEFRAMES:
        try:
            df = fetch_timeframe(symbol, timeframe)

            if df.empty:
                print(f"[WARN] {symbol} {timeframe}: no data returned")
                continue

            df["symbol"] = symbol
            df["timeframe"] = timeframe
            save_candles(df[[
                "symbol", "timeframe", "datetime",
                "open", "high", "low", "close", "volume"
            ]])

            print(f"[OK] {symbol} {timeframe}: {len(df)} candles")

        except Exception as exc:
            print(f"[ERROR] {symbol} {timeframe}: {exc}")


def update_all() -> None:
    """Fetch each symbol once; all configured timeframes are created locally."""
    if not API_KEY:
        print("[ERROR] TWELVE_API_KEY is missing")
        return

    for symbol in SYMBOLS:
        update_symbol(symbol)
