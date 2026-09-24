from twelvedata import TDClient
import pandas as pd

from config import API_KEY
from config import SYMBOLS
from config import TIMEFRAMES

from core.database import engine

td = TDClient(apikey=API_KEY)

def fetch(symbol,timeframe):

    ts = td.time_series(
        symbol=symbol,
        interval=timeframe,
        outputsize=500
    )

    df = ts.as_pandas()

    df = df.reset_index()

    df = df.rename(columns={
        "datetime":"datetime"
    })

    df["symbol"] = symbol
    df["timeframe"] = timeframe

    cols = [
        "symbol",
        "timeframe",
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    df = df[cols]

    df.to_sql(
        "candles",
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    print(symbol,timeframe,len(df))

def update_all():

    for s in SYMBOLS:
        for tf in TIMEFRAMES:

            try:
                fetch(s,tf)

            except Exception as e:

                print(e)