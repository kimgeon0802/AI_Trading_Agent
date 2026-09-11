import pytest
import pandas as pd
import numpy as np
from market.market_data_adapter import MarketDataAdapter

def test_market_data_adapter():
    adapter = MarketDataAdapter()
    
    # Mock Candidate DataFrame
    data = {
        'ticker': ['000660'],
        'name': ['SK하이닉스'],
        'market': ['KOSPI'],
        'close': [300000.0],
        'change': [5000.0],
        'change_rate': [1.69],
        'volume': [1000000],
        'market_cap': [200000000000],
        'trading_value': [300000000000],
        'screening_score': [85.0]
    }
    candidate_df = pd.DataFrame(data)
    
    # Mock Historical Data
    hist_data = {
        'close': np.linspace(290000, 300000, 30),
        'change_rate': np.random.uniform(-1, 1, 30),
        'volume': np.random.randint(1000, 5000, 30)
    }
    historical_data_map = {'000660': pd.DataFrame(hist_data)}
    
    results = adapter.convert_candidates(candidate_df, historical_data_map=historical_data_map)
    
    assert len(results) == 1
    item = results[0]
    
    assert item["ticker"] == '000660'
    assert "price_data" in item
    assert "technical" in item
    assert "returns" in item
    assert "screening_context" in item
    assert item["screening_context"]["screening_score"] == 85.0
    assert item["technical"]["RSI"] is not None
