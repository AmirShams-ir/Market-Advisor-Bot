from __future__ import annotations

from dataclasses import dataclass, field

from config import DEFAULT_TIMEFRAMES
from core.fetcher import collect_symbol


@dataclass
class SymbolConfig:
    symbol: str
    timeframes: list[str] = field(default_factory=lambda: list(DEFAULT_TIMEFRAMES))
    auto_update: bool = False


def prompt_symbol() -> SymbolConfig:
    symbol = input("Enter symbol (e.g. BTC/USD): ").strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty")

    print("Available timeframes:", ", ".join(DEFAULT_TIMEFRAMES))
    raw = input("Timeframes [1h,4h,1day,1week]: ").strip()
    timeframes = [x.strip() for x in raw.split(",")] if raw else list(DEFAULT_TIMEFRAMES)

    invalid = [x for x in timeframes if x not in DEFAULT_TIMEFRAMES]
    if invalid:
        raise ValueError(f"Unsupported timeframe(s): {', '.join(invalid)}")

    raw_auto = input(f"Enable scheduled updates for {symbol}? [y/N]: ").strip().lower()
    auto_update = raw_auto in {"y", "yes"}

    return SymbolConfig(symbol=symbol, timeframes=timeframes, auto_update=auto_update)


def setup_symbol() -> SymbolConfig:
    config = prompt_symbol()

    print(f"[BOOTSTRAP] Collecting historical data for {config.symbol}...")
    collect_symbol(config.symbol, timeframes=config.timeframes)

    return config
