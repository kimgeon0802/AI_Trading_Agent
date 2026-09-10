import pytest
from runtime.tool_manager.position_sizer import PositionSizer

def test_calculate_target_positions_basic():
    sizer = PositionSizer()
    buy_candidates = [
        {"ticker": "A", "confidence": 0.9},
        {"ticker": "B", "confidence": 0.9}
    ]
    portfolio = {"cash": 1000000} # 100만
    holdings = []
    
    targets = sizer.calculate_target_positions(buy_candidates, portfolio, holdings)
    
    # investable cash = 80만
    # A, B 각 40만
    assert targets["A"] == 400000
    assert targets["B"] == 400000

def test_calculate_target_positions_confidence_scaling():
    sizer = PositionSizer()
    buy_candidates = [
        {"ticker": "A", "confidence": 0.9},
        {"ticker": "B", "confidence": 0.5} # Should be scaled down
    ]
    portfolio = {"cash": 1000000}
    holdings = []
    
    targets = sizer.calculate_target_positions(buy_candidates, portfolio, holdings)
    
    # 0.5 confidence -> base weight * 0.5
    # weight_A = 0.5 * 0.9 = 0.45
    # weight_B = 0.5 * 0.5 = 0.25
    # total = 0.7
    # weight_A_norm = 0.45 / 0.7 = 0.6428
    # weight_B_norm = 0.25 / 0.7 = 0.3571
    
    assert targets["A"] > targets["B"]
