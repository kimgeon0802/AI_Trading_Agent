import pytest
import pandas as pd
import numpy as np
from market.screening_engine import ScreeningEngine, ScreeningConfig
from runtime.tool_manager.refinement_engine import RefinementEngine

def generate_mock_market_data(num_stocks=200):
    data = {
        "ticker": [f"T{i}" for i in range(num_stocks)],
        "name": [f"Name{i}" for i in range(num_stocks)],
        "market": ["KOSPI"] * num_stocks,
        "open": np.random.rand(num_stocks) * 100,
        "high": np.random.rand(num_stocks) * 100,
        "low": np.random.rand(num_stocks) * 100,
        "close": np.random.rand(num_stocks) * 100,
        "change": np.random.rand(num_stocks),
        "change_rate": np.random.uniform(-10, 10, num_stocks),
        "volume": np.random.rand(num_stocks) * 1000,
        "trading_value": np.random.rand(num_stocks) * 1000000000,
        "market_cap": np.random.rand(num_stocks) * 100000000000,
        "shares": np.random.rand(num_stocks) * 10000,
        "data_date": ["2026-09-10"] * num_stocks,
        "collected_at": ["2026-09-10 19:00:00"] * num_stocks,
    }
    return pd.DataFrame(data)

def test_mock_pipeline_screening_to_refinement():
    # 1. Generate Data (Screening input)
    market_df = generate_mock_market_data(num_stocks=200)
    
    # 2. Run Screening
    engine = ScreeningEngine(ScreeningConfig(top_n=50))
    df = engine.validate_market_data(market_df)
    df = engine.filter_liquidity(df)
    df = engine.filter_market_cap(df)
    df = engine.filter_extreme_change(df)
    df = engine.calculate_liquidity_score(df)
    df = engine.calculate_momentum_score(df)
    df = engine.calculate_market_cap_score(df)
    df = engine.calculate_total_score(df)
    candidates = engine.select_candidates(df)
    
    # 3. Run Refinement
    refiner = RefinementEngine(target_min=10, target_max=15)
    refined = refiner.refine(candidates)
    
    # 4. Verify
    assert len(refined) <= 15
    assert "screening_score" in refined.columns
    # Check that refined candidates are a subset of screening candidates
    assert set(refined["ticker"]).issubset(set(candidates["ticker"]))
