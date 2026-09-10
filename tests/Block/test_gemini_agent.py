import pytest
from unittest.mock import MagicMock
from agents.gemini_agent.agent import GeminiAgent
import os

def test_gemini_agent_init():
    os.environ["USE_MOCK_AI"] = "true"
    agent = GeminiAgent()
    assert agent.client is None

def test_gemini_agent_make_decision_mock():
    os.environ["USE_MOCK_AI"] = "true"
    agent = GeminiAgent()
    market_data = {"name": "SK하이닉스"}
    decision = agent.make_decision(market_data)
    
    assert decision is not None
    assert "decision" in decision
    assert decision["decision"] in ["BUY", "SELL", "HOLD"]
