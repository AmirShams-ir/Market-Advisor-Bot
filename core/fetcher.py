from __future__ import annotations

from typing import Dict

import pandas as pd
from twelvedata import TDClient

from config import API_KEY, BASE_TIMEFRAME, SYMBOLS, TIMEFRAMES
from core.database import engine

td = TDClient(apikey=API_KEY)

# Twelve Data intervals map to pandas resampling rules.
RESAMPLE_RULES: Dict[str, str] = {
    "1min": "1min",
    "5min": "5min",
    "15min": "15min",
    "1h": "1h",
    "4h": "4h",
}


def fetch_base(symbol: str) -> pd.DataFrame:
    """Fetch the base timeframe once for a symbol."""
    ts = td.time_series(
        symbol=symbol,
        interval=BASE_TIMEFRAME,
        outputsize=500,
    )
    df = ts.as_pandas().reset_index()

    if df.empty:
        return df

    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    for column in ("open", "high", "low", "close", "volume"):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df.dropna(subset=["datetime", "open", "high", "low", "close"])


def resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Build a higher timeframe locally from the base OHLCV data."""
    if timeframe == BASE_TIMEFRAME:
        result = df.copy()
    else:
        rule = RESAMPLE_RULES[timeframe]
        work = df.set_index("datetime").sort_index()

        result = (
            work.resample(rule, label="left", closed="left")
            .agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                }
            )
            .dropna(subset=["open", "high", "low", "close"])
            .reset_index()
        )

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
    """Use one Twelve Data call per symbol, then build all timeframes locally."""
    try:
        base = fetch_base(symbol)

        if base.empty:
            print(f"[WARN] {symbol}: no data returned")
            return

        base["symbol"] = symbol

        for timeframe in TIMEFRAMES:
            candles = resample_ohlcv(base, timeframe)
            save_candles(candles)
            print(
                f"[OK] {symbol} {timeframe}: "
                f"{len(candles)} candles (local)"
            )

    except Exception as exc:
        print(f"[ERROR] {symbol}: {exc}")


def update_all() -> None:
    """Fetch each symbol once; all configured timeframes are created locally."""
    if not API_KEY:
        print("[ERROR] TWELVE_API_KEY is missing")
        return

    for symbol in SYMBOLS:
        update_symbol(symbol)
