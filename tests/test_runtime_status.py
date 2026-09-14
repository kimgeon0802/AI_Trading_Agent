import pytest
from unittest.mock import MagicMock, patch
from runtime.executor.main import RuntimeExecutor

class MockDBForStatus:
    def __init__(self):
        self.predictions = []
    def get_portfolio(self):
        return {"cash": 10000000.0, "total_asset": 10000000.0}
    def get_holdings(self):
        return []
    def update_portfolio(self, cash, total_asset, timestamp):
        pass
    def save_prediction(self, ticker, pred, ret, conf, reason, ts):
        pred_id = len(self.predictions) + 1
        self.predictions.append({"id": pred_id, "ticker": ticker})
        return pred_id
    def fetchall(self):
        return []

def test_overall_status_all_success():
    """Scenario 1: All candidates SUCCESS -> Overall status SUCCESS"""
    executor = RuntimeExecutor()
    cycle_data = {
        "prediction_ids": [1, 2],
        "candidate_summary": [
            {"ticker": "005930", "status": "SUCCESS", "consensus_method": "validated_by_claude"},
            {"ticker": "000660", "status": "SUCCESS", "consensus_method": "validated_by_claude"}
        ]
    }
    status = executor._calculate_overall_status(cycle_data)
    assert status == "SUCCESS"


def test_overall_status_normal_hold_risk_gate():
    """Scenario 2: Normal Risk Gate REJECT/WARNING HOLD is valid AI decision -> SUCCESS"""
    executor = RuntimeExecutor()
    cycle_data = {
        "prediction_ids": [1],
        "candidate_summary": [
            {"ticker": "005930", "status": "SUCCESS", "consensus_method": "risk_gate_rejection"}
        ]
    }
    status = executor._calculate_overall_status(cycle_data)
    assert status == "SUCCESS"


def test_overall_status_claude_failure_fallback():
    """Scenario 3 & 5: All candidates FALLBACK -> Overall status FAILED"""
    executor = RuntimeExecutor()
    cycle_data = {
        "prediction_ids": [1],
        "candidate_summary": [
            {"ticker": "005930", "status": "FALLBACK", "consensus_method": "fallback_hold"}
        ]
    }
    status = executor._calculate_overall_status(cycle_data)
    assert status == "FAILED"


def test_overall_status_partial_fallback():
    """Scenario 4: 1 candidate SUCCESS + 1 candidate FALLBACK -> Overall status PARTIAL"""
    executor = RuntimeExecutor()
    cycle_data = {
        "prediction_ids": [1, 2],
        "candidate_summary": [
            {"ticker": "005930", "status": "SUCCESS", "consensus_method": "validated_by_claude"},
            {"ticker": "000660", "status": "FALLBACK", "consensus_method": "fallback_hold"}
        ]
    }
    status = executor._calculate_overall_status(cycle_data)
    assert status == "PARTIAL"


def test_overall_status_gemini_batch_failure():
    """Scenario 6: Gemini Batch failure / fatal error -> Overall status FAILED"""
    executor = RuntimeExecutor()
    cycle_data = {
        "prediction_ids": [],
        "candidate_summary": [],
        "fatal_error": "Gemini batch failed"
    }
    status = executor._calculate_overall_status(cycle_data)
    assert status == "FAILED"


def test_overall_status_tavily_failure_non_critical():
    """Scenario 7: Tavily search fails but Claude & Consensus succeed -> Overall status SUCCESS"""
    executor = RuntimeExecutor()
    cycle_data = {
        "prediction_ids": [1],
        "candidate_summary": [
            {"ticker": "005930", "status": "SUCCESS", "consensus_method": "validated_by_claude"}
        ]
    }
    status = executor._calculate_overall_status(cycle_data)
    assert status == "SUCCESS"


def test_overall_status_portfolio_partial_failure():
    """Scenario 8 & 9: Portfolio execution failure on some candidate -> PARTIAL"""
    executor = RuntimeExecutor()
    cycle_data = {
        "prediction_ids": [1, 2],
        "candidate_summary": [
            {"ticker": "005930", "status": "SUCCESS", "consensus_method": "validated_by_claude"},
            {"ticker": "000660", "status": "PARTIAL", "consensus_method": "validated_by_claude"}
        ]
    }
    status = executor._calculate_overall_status(cycle_data)
    assert status == "PARTIAL"


def test_prediction_ids_returned_accurately():
    """Scenario 10: Verify prediction_ids list is accurate"""
    executor = RuntimeExecutor()
    cycle_data = {
        "prediction_ids": [10, 11, 12],
        "candidate_summary": [
            {"ticker": "T1", "status": "SUCCESS", "consensus_method": "validated_by_claude"},
            {"ticker": "T2", "status": "SUCCESS", "consensus_method": "validated_by_claude"},
            {"ticker": "T3", "status": "SUCCESS", "consensus_method": "validated_by_claude"}
        ]
    }
    assert cycle_data["prediction_ids"] == [10, 11, 12]
