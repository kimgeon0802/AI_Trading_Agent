import pytest
from unittest.mock import MagicMock
from agents.multi_ai.orchestrator import MultiAIOrchestrator
from runtime.tool_manager.api_error_handler import APIStatus
import os

class MockDB:
    def save_agent_decision(self, *args, **kwargs):
        pass

def test_full_pipeline_integration():
    os.environ["USE_MOCK_AI"] = "true"
    db = MockDB()
    orchestrator = MultiAIOrchestrator(db)
    
    # Mock ClaudeAgent to return successful evaluation
    orchestrator.claude_agent.make_decision = MagicMock(return_value={
        "evaluation": "PASS",
        "score": 85,
        "reasoning": "Mock evaluation",
        "issues": [],
        "risk_level": "LOW"
    })
    
    # Mock ConsensusManager
    orchestrator.consensus_manager.get_consensus = MagicMock(return_value={
        "decision": "BUY",
        "confidence": 0.85,
        "reasoning": "Consensus reached",
        "method": "weighted_average"
    })
    
    market_data = {
        "timestamp": "2026-09-10",
        "market_summary": {"condition": "bullish"},
        "macro_data": {}
    }
    
    # Execute full pipeline
    orchestrator.tavily_provider = MagicMock()
    orchestrator.tavily_provider.search.return_value = (APIStatus.SUCCESS, [])
    
    result = orchestrator.execute(market_data, prediction_id=1)
    
    # Verify
    assert result is not None
    assert result["decision"] == "BUY"
    assert "gemini" in result["agent_results"]
    assert "claude" in result["agent_results"]
    
    # Verify Tavily was called
    orchestrator.tavily_provider.search.assert_called()
