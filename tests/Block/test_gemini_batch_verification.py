import json
import os
import pytest
from unittest.mock import MagicMock
from agents.gemini_agent.agent import GeminiAgent
from agents.multi_ai.orchestrator import MultiAIOrchestrator

def test_gemini_batch_call_count():
    # Setup
    os.environ["USE_MOCK_AI"] = "false"
    gemini_agent = GeminiAgent(system_prompt_path="prompts/system_prompt.md", decision_prompt_path="prompts/decision_prompt.md")
    gemini_agent.client = MagicMock() # Mock the client
    
    # Dummy data (multiple candidates)
    market_data_list = [{"ticker": "005930"}, {"ticker": "000660"}]
    
    # Configure mock to return valid JSON
    gemini_agent.client.models.generate_content.return_value.text = json.dumps({
        "analyses": [
            {"ticker": "005930", "decision": "BUY", "confidence": 0.8},
            {"ticker": "000660", "decision": "HOLD", "confidence": 0.5}
        ],
        "selected_candidates": [
            {"ticker": "005930", "priority": "HIGH"}
        ]
    })
    
    # Execute Batch
    result = gemini_agent.execute_batch(market_data_list)
    
    # Verification
    assert gemini_agent.client.models.generate_content.call_count == 1
    assert len(result["selected_candidates"]) == 1
    assert result["selected_candidates"][0]["ticker"] == "005930"
