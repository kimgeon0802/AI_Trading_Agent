import pytest
import pandas as pd
import numpy as np
from market.technical_analysis import TechnicalAnalysisEngine

def test_technical_analysis_engine():
    engine = TechnicalAnalysisEngine()
    
    # Create mock data
    dates = pd.date_range(start='2026-01-01', periods=100)
    data = {
        'close': np.linspace(100, 200, 100),
        'change_rate': np.random.uniform(-1, 1, 100),
        'volume': np.random.randint(1000, 5000, 100)
    }
    df = pd.DataFrame(data, index=dates)
    
    results = engine.calculate(df)
    
    assert "returns" in results
    assert "technical" in results
    assert "volume" in results
    
    # Check if values are calculated (not None) for sufficient data
    assert results["returns"]["1d"] is not None
    assert results["technical"]["MA20"] is not None
    assert results["technical"]["RSI"] is not None
    assert results["technical"]["MACD"]["MACD"] is not None
    assert results["volume"]["relative"] is not None

def test_technical_analysis_engine_insufficient_data():
    engine = TechnicalAnalysisEngine()
    
    # Data too short
    df = pd.DataFrame({'close': [100, 101], 'change_rate': [1, 1], 'volume': [100, 200]})
    
    results = engine.calculate(df)
    
    assert results["technical"]["MA60"] is None
    assert results["technical"]["RSI"] is None
