import os
from datetime import datetime
from pykrx import stock
import pandas as pd

def diagnose():
    # 20260909 (today, based on context)
    date = "20260909"
    ticker = "005930"
    market = "KOSPI"

    print(f"--- Diagnosing Ticker: {ticker} ({market}) on {date} ---")

    # [1] Raw OHLCV
    print(f"\n[1] Testing get_market_ohlcv_by_ticker:")
    ohlcv = stock.get_market_ohlcv_by_ticker(date)
    print(f"Result type: {type(ohlcv)}")
    print(ohlcv.head())

    # [2] Raw Market Cap
    print(f"\n[2] Testing get_market_cap_by_ticker:")
    # This likely expects ticker as an argument according to the error in [1] earlier, or maybe it returns market-wide. Let me check get_market_cap_by_ticker docstring.
    # Actually, for now, let's fix the known invalid calls.
    cap = stock.get_market_cap_by_ticker(date)
    print(f"Result type: {type(cap)}")
    print(cap.head())

    # [3] Collector OHLCV Logic Simulation (from collector code)
    print(f"\n[3] Simulating Collector OHLCV logic:")
    try:
        # The collector uses stock.get_market_ohlcv_by_ticker(request_date, market=market)
        df_market = stock.get_market_ohlcv_by_ticker(date, market=market)
        print(f"Market OHLCV DataFrame sample (head):")
        print(df_market.head(5))
        print(f"Are all values zero? { (df_market == 0).all().all() }")
    except Exception as e:
        print(f"Error simulating: {e}")

if __name__ == "__main__":
    diagnose()
