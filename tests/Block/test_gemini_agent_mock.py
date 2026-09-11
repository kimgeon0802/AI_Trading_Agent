import os
import pytest
from agents.gemini_agent.agent import GeminiAgent

def test_gemini_agent_mock_decision():
    # Set mock mode
    os.environ["USE_MOCK_AI"] = "true"
    
    agent = GeminiAgent()
    
    mock_data = {"ticker": "000660", "name": "SK하이닉스"}
    
    results = agent.make_decision(mock_data)
    
    # Check if mock returned results
    assert results is not None
    # Check structure
    assert results["ticker"] == "000660"
