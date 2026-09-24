from pathlib import Path
import re

from sqlalchemy import create_engine, text

from config import DATA_DIR

Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(parents=True, exist_ok=True)


def symbol_db_path(symbol: str) -> Path:
    """Return the SQLite file dedicated to one symbol."""
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", symbol)
    return Path(DATA_DIR) / f"{safe}.db"


def get_engine(symbol: str):
    """Create an engine for the symbol-specific SQLite database."""
    return create_engine(f"sqlite:///{symbol_db_path(symbol)}")


def create_symbol_tables(symbol: str) -> None:
    engine = get_engine(symbol)

    sql = """
    CREATE TABLE IF NOT EXISTS candles (
        timeframe TEXT,
        datetime TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL,
        PRIMARY KEY(timeframe, datetime)
    );
    """

    with engine.begin() as conn:
        conn.execute(text(sql))
