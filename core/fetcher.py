from __future__ import annotations

import argparse
import pandas as pd
from twelvedata import TDClient

from config import API_KEY, DEFAULT_EXCHANGE, DEFAULT_TIMEFRAMES, FETCH_OUTPUTSIZE
from core.database import create_symbol_tables, get_engine

td = TDClient(apikey=API_KEY)


def fetch_timeframe(symbol: str, timeframe: str) -> pd.DataFrame:
    ts = td.time_series(
        symbol=symbol,
        exchange=DEFAULT_EXCHANGE,
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


def collect_symbol(symbol: str, timeframes=None) -> None:
    selected = timeframes or DEFAULT_TIMEFRAMES
    create_symbol_tables(symbol)

    print(f"[SYMBOL] {symbol}")
    print(f"[DB] data/{symbol.replace('/', '_')}.db")

    for timeframe in selected:
        try:
            df = fetch_timeframe(symbol, timeframe)
            count = save_candles(df, symbol, timeframe)

            if count:
                print(f"[OK] {symbol} {timeframe}: {count} candles")
            else:
                print(f"[WARN] {symbol} {timeframe}: no data")
        except Exception as exc:
            print(f"[ERROR] {symbol} {timeframe}: {exc}")


def update_symbol_timeframe(symbol: str, timeframe: str) -> None:
    try:
        df = fetch_timeframe(symbol, timeframe)
        count = save_candles(df, symbol, timeframe)
        print(f"[UPDATE] {symbol} {timeframe}: {count} candles")
    except Exception as exc:
        print(f"[ERROR] {symbol} {timeframe}: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Market Advisor Bot candle data")
    parser.add_argument("--symbol", required=True, help="Twelve Data symbol, e.g. BTC/USD")
    parser.add_argument("--timeframe", help="Fetch only one timeframe")
    parser.add_argument(
        "--bootstrap",
        action="store_true",
        help="Fetch all default timeframes for the symbol",
    )
    args = parser.parse_args()

    if not API_KEY:
        raise SystemExit("TWELVE_API_KEY is missing")

    if args.bootstrap or not args.timeframe:
        collect_symbol(args.symbol)
    else:
        update_symbol_timeframe(args.symbol, args.timeframe)


if __name__ == "__main__":
    main()
