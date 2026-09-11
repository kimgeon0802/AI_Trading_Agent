import pytest
import pandas as pd
import numpy as np
import json
from market.market_data_collector import MarketDataCollector
from market.market_data_adapter import MarketDataAdapter

def test_pipeline_integration_sample_dataset():
    collector = MarketDataCollector()
    adapter = MarketDataAdapter()
    
    # Use a real ticker for sample data
    ticker = "005930" 
    
    # 1. Fetch historical data
    hist_df = collector.get_historical_ohlcv(ticker, days=100)
    
    # 2. Mock candidate data
    candidate_data = {
        'ticker': [ticker],
        'name': ['삼성전자'],
        'market': ['KOSPI'],
        'close': [hist_df['close'].iloc[-1]],
        'change': [hist_df['close'].iloc[-1] - hist_df['close'].iloc[-2]],
        'change_rate': [hist_df['change_rate'].iloc[-1]],
        'volume': [hist_df['volume'].iloc[-1]],
        'market_cap': [1000000000000],
        'trading_value': [10000000000],
        'screening_score': [90.0]
    }
    candidate_df = pd.DataFrame(candidate_data)
    
    # 3. Create historical map
    historical_data_map = {ticker: hist_df}
    
    # 4. Convert to dataset
    dataset = adapter.convert_candidates(candidate_df, historical_data_map=historical_data_map)
    
    # 5. Validate structure
    assert len(dataset) == 1
    sample = dataset[0]
    
    # Output sample for verification
    print("\n--- Gemini Analysis Dataset Sample ---")
    print(json.dumps(sample, indent=2, ensure_ascii=False))
    
    assert "technical" in sample
    assert sample["technical"]["RSI"] is not None
    assert sample["technical"]["MA20"] is not None
    assert "returns" in sample
    assert sample["returns"]["60d"] is not None

if __name__ == "__main__":
    test_pipeline_integration_sample_dataset()
