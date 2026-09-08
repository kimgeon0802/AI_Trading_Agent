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
    ohlcv = stock.get_market_ohlcv_by_ticker(date, ticker=ticker)
    print(f"Result type: {type(ohlcv)}")
    print(ohlcv)
    if not ohlcv.empty:
        print(f"Close value: {ohlcv.iloc[0].get('종가', 'N/A')}")
    else:
        print("DataFrame is empty.")

    # [2] Raw Market Cap
    print(f"\n[2] Testing get_market_cap_by_ticker:")
    cap = stock.get_market_cap_by_ticker(date, ticker=ticker)
    print(f"Result type: {type(cap)}")
    print(cap)
    if not cap.empty:
        print(f"Market Cap value: {cap.iloc[0].get('시가총액', 'N/A')}")
    else:
        print("DataFrame is empty.")

    # [3] Collector OHLCV Logic Simulation (from collector code)
    print(f"\n[3] Simulating Collector OHLCV logic:")
    try:
        # Based on collector logic for individual ticker
        df = stock.get_market_ohlcv_by_ticker(date, ticker=ticker)
        # Note: collector handles entire market, not single ticker in the main loop,
        # but the logic for renaming should be consistent.
        # The collector uses stock.get_market_ohlcv_by_ticker(request_date, market=market)
        # Let's test the market-wide call which is what collector does
        df_market = stock.get_market_ohlcv_by_ticker(date, market=market)
        print(f"Market OHLCV DataFrame sample (head):")
        print(df_market.head(5))
        print(f"Are all values zero? { (df_market == 0).all().all() }")
    except Exception as e:
        print(f"Error simulating: {e}")

if __name__ == "__main__":
    diagnose()
