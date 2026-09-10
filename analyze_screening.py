import pandas as pd
import numpy as np
from scripts.generate_mock_data import generate_mock_data
from market.screening_engine import ScreeningEngine, ScreeningConfig

# 1. Generate Mock Data
market_df = generate_mock_data(num_stocks=200)

# 2. Run Screening
engine = ScreeningEngine(ScreeningConfig(top_n=50))
validated_df = engine.validate_market_data(market_df)
liquidity_df = engine.filter_liquidity(validated_df)
cap_df = engine.filter_market_cap(liquidity_df)
change_df = engine.filter_extreme_change(cap_df)

if not change_df.empty:
    scored_df = engine.calculate_liquidity_score(change_df)
    scored_df = engine.calculate_momentum_score(scored_df)
    scored_df = engine.calculate_market_cap_score(scored_df)
    scored_df = engine.calculate_total_score(scored_df)
    candidates = engine.select_candidates(scored_df)

    # 3. Perform Analysis
    print("후보 수:", len(candidates))
    print("Score 평균:", candidates["screening_score"].mean())
    print("Score 중앙값:", candidates["screening_score"].median())
    print("Score 표준편차:", candidates["screening_score"].std())
    
    top_10 = candidates.head(10)
    rest_40 = candidates.tail(40)
    
    print("Top 10 평균:", top_10["screening_score"].mean())
    print("11~50 평균:", rest_40["screening_score"].mean())
    
    print("10위 Score:", candidates.iloc[9]["screening_score"])
    print("11위 Score:", candidates.iloc[10]["screening_score"])
    print("Score Gap:", candidates.iloc[9]["screening_score"] - candidates.iloc[10]["screening_score"])
    
    print("\n지표별 영향력 (상관관계):")
    print(candidates[["screening_score", "liquidity_score", "momentum_score", "market_cap_score"]].corr()["screening_score"])
    
    print("\n시장별 분포:")
    print(candidates["market"].value_counts())
else:
    print("No candidates found")
