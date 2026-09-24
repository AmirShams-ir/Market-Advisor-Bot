from __future__ import annotations

import pandas as pd
from twelvedata import TDClient

from config import API_KEY, DEFAULT_EXCHANGE, DEFAULT_TIMEFRAMES, FETCH_OUTPUTSIZE
from core.database import create_symbol_tables, get_engine

td = TDClient(apikey=API_KEY)


def fetch_timeframe(symbol: str, timeframe: str, exchange: str = DEFAULT_EXCHANGE) -> pd.DataFrame:
    ts = td.time_series(
        symbol=symbol,
        exchange=exchange,
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

    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    else:
        df["volume"] = 0.0

    return df.dropna(subset=["datetime", "open", "high", "low", "close"])


def save_candles(df: pd.DataFrame, symbol: str, timeframe: str) -> int:
    if df.empty:
        return 0

    create_symbol_tables(symbol)
    engine = get_engine(symbol)

    with engine.begin() as conn:
        for row in df.to_dict(orient="records"):
            conn.exec_driver_sql(
                """
                INSERT OR REPLACE INTO candles
                (timeframe, datetime, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    timeframe,
                    row["datetime"].isoformat(),
                    float(row["open"]),
                    float(row["high"]),
                    float(row["low"]),
                    float(row["close"]),
                    float(row["volume"]) if pd.notna(row["volume"]) else None,
                ),
            )

    return len(df)


def collect_symbol(symbol: str, exchange: str = DEFAULT_EXCHANGE, timeframes=None) -> None:
    selected = timeframes or DEFAULT_TIMEFRAMES
    create_symbol_tables(symbol)

    print(f"[SYMBOL] {symbol} ({exchange})")

    for timeframe in selected:
        try:
            df = fetch_timeframe(symbol, timeframe, exchange)
            count = save_candles(df, symbol, timeframe)

            if count:
                print(f"[OK] {symbol} {timeframe}: {count} candles")
            else:
                print(f"[WARN] {symbol} {timeframe}: no data")

        except Exception as exc:
            print(f"[ERROR] {symbol} {timeframe}: {exc}")
