from __future__ import annotations

import time

import schedule

from config import TIMEFRAMES
from core.fetcher import update_all

# The schedule is intentionally a little after the candle boundary so the
# newly closed candle has time to become available at the provider.
REFRESH_MINUTES = {
    "1h": 61,
    "4h": 241,
    "1day": 24 * 60 + 1,
    "1week": 7 * 24 * 60 + 1,
}


def schedule_updates() -> None:
    for timeframe in TIMEFRAMES:
        minutes = REFRESH_MINUTES[timeframe]
        schedule.every(minutes).minutes.do(update_all)


def run() -> None:
    update_all()
    schedule_updates()

    print("[RUNNING] Market Advisor Bot data collector")

    while True:
        schedule.run_pending()
        time.sleep(1)
