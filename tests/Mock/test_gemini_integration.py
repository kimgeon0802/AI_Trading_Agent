import pytest
from unittest.mock import MagicMock
from agents.multi_ai.orchestrator import MultiAIOrchestrator
import os

class MockDB:
    def save_agent_decision(self, *args, **kwargs):
        pass

def test_gemini_integration():
    os.environ["USE_MOCK_AI"] = "true"
    db = MockDB()
    orchestrator = MultiAIOrchestrator(db)
    
    market_data = {
        "timestamp": "2026-09-10",
        "market_summary": {"condition": "bullish"},
        "macro_data": {}
    }
    
    result = orchestrator.execute(market_data, prediction_id=1)
    
    assert result is not None
    assert "consensus" in result
    assert "agent_results" in result
    assert "gemini" in result["agent_results"]
    assert "claude" in result["agent_results"]
