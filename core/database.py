from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy import text

from config import DATABASE

# SQLite cannot create its parent directory automatically.
Path("data").mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(parents=True, exist_ok=True)

engine = create_engine(DATABASE)


def create_tables():
    sql = """
    CREATE TABLE IF NOT EXISTS candles (
        symbol TEXT,
        timeframe TEXT,
        datetime TEXT,

        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL,

        PRIMARY KEY(symbol, timeframe, datetime)
    );
    """

    with engine.begin() as conn:
        conn.execute(text(sql))
