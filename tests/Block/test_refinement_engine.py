import pytest
import pandas as pd
import numpy as np
from runtime.tool_manager.refinement_engine import RefinementEngine

@pytest.fixture
def mock_candidates():
    # 50개의 더미 후보 데이터 생성
    data = {
        "ticker": [f"T{i}" for i in range(50)],
        "screening_score": np.linspace(0, 100, 50)
    }
    return pd.DataFrame(data)

def test_refinement_standard(mock_candidates):
    engine = RefinementEngine(target_min=10, target_max=15)
    refined = engine.refine(mock_candidates)
    
    assert 10 <= len(refined) <= 15
    assert refined.iloc[0]["screening_score"] == 100.0 # 상위 점수 확인

def test_refinement_small_input():
    # 5개만 있는 경우
    data = {"ticker": ["T1", "T2", "T3", "T4", "T5"], "screening_score": [10, 20, 30, 40, 50]}
    df = pd.DataFrame(data)
    engine = RefinementEngine(target_min=10, target_max=15)
    refined = engine.refine(df)
    
    assert len(refined) == 5

def test_refinement_missing_data():
    # Sector 등이 없는 경우 Graceful degradation 확인
    data = {"ticker": [f"T{i}" for i in range(50)], "screening_score": np.linspace(0, 100, 50)}
    df = pd.DataFrame(data)
    engine = RefinementEngine(target_min=10, target_max=15)
    
    # 예외 발생 없이 동작해야 함
    try:
        refined = engine.refine(df)
        assert len(refined) <= 15
    except Exception as e:
        pytest.fail(f"Refinement failed with missing sector data: {e}")
