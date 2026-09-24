from __future__ import annotations

import time
from datetime import timedelta

import schedule

from core.fetcher import fetch_timeframe, save_candles


REFRESH_DELTA = {
    "1h": timedelta(hours=1, minutes=1),
    "4h": timedelta(hours=4, minutes=1),
    "1day": timedelta(days=1, minutes=1),
    "1week": timedelta(days=7, minutes=1),
}


def update_symbol_timeframe(symbol: str, exchange: str, timeframe: str) -> None:
    try:
        df = fetch_timeframe(symbol, timeframe, exchange)
        count = save_candles(df, symbol, timeframe)
        print(f"[UPDATE] {symbol} {timeframe}: {count} candles refreshed")
    except Exception as exc:
        print(f"[ERROR] {symbol} {timeframe}: {exc}")


def schedule_symbol(config) -> None:
    for timeframe in config.timeframes:
        delay = REFRESH_DELTA[timeframe]
        schedule.every(delay.total_seconds() / 60).minutes.do(
            update_symbol_timeframe,
            config.symbol,
            config.exchange,
            timeframe,
        )
        print(f"[TIMER] {config.symbol} {timeframe}: every {delay}")


def run_scheduled(configs) -> None:
    enabled = [c for c in configs if c.auto_update]

    if not enabled:
        print("[IDLE] Scheduled updates disabled")
        return

    for config in enabled:
        schedule_symbol(config)

    print("[RUNNING] Market Advisor Bot scheduler")

    while True:
        schedule.run_pending()
        time.sleep(1)
