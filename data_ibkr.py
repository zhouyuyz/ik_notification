import pandas as pd
from ib_insync import IB, Stock, util

def connect_ibkr(host: str, port: int, client_id: int) -> IB:
    ib = IB()
    ib.connect(host, port, clientId=client_id)
    return ib

def fetch_bars(
    ib: IB,
    symbol: str,
    bar_size: str,
    duration: str,
    use_rth: bool = True,
) -> pd.DataFrame:
    contract = Stock(symbol, "SMART", "USD")
    ib.qualifyContracts(contract)

    bars = ib.reqHistoricalData(
        contract,
        endDateTime="",
        durationStr=duration,
        barSizeSetting=bar_size,
        whatToShow="TRADES",
        useRTH=use_rth,
        formatDate=1,
    )
    df = util.df(bars)
    if df.empty:
        raise RuntimeError("No bars returned. Check symbol/connection/time settings.")
    df = df.rename(columns={"date": "datetime"})
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)
    return df
