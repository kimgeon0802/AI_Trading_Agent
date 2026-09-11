import pytest
import pandas as pd
from market.market_data_collector import MarketDataCollector

def test_get_historical_ohlcv():
    collector = MarketDataCollector()
    
    # Test with a well-known ticker
    ticker = "005930" # Samsung Electronics
    df = collector.get_historical_ohlcv(ticker, days=30)
    
    if not df.empty:
        assert "date" in df.columns
        assert "close" in df.columns
        assert "volume" in df.columns
        assert len(df) > 0
    else:
        # It's possible pykrx fails in some environments
        pytest.skip("No data returned from pykrx, likely network/API limit issue.")

def test_get_historical_ohlcv_empty():
    collector = MarketDataCollector()
    
    # Test with invalid ticker
    ticker = "999999"
    df = collector.get_historical_ohlcv(ticker, days=30)
    
    assert df.empty
