import pytest
import os
from unittest.mock import MagicMock
from agents.gemini_agent.agent import GeminiAgent

def test_gemini_parse_pure_json(monkeypatch):
    monkeypatch.setenv("USE_MOCK_AI", "false")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_key")
    
    # Mock GenAI client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"analyses": [{"ticker": "005930"}], "selected_candidates": [{"ticker": "005930"}]}'
    mock_client.models.generate_content.return_value = mock_response
    
    agent = GeminiAgent()
    agent.client = mock_client
    
    result = agent.execute_batch([{"ticker": "005930"}])
    assert "analyses" in result
    assert len(result["analyses"]) == 1

def test_gemini_parse_markdown_json_wrapper(monkeypatch):
    monkeypatch.setenv("USE_MOCK_AI", "false")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_key")
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '```json\n{"analyses": [{"ticker": "000660"}], "selected_candidates": [{"ticker": "000660"}]}\n```'
    mock_client.models.generate_content.return_value = mock_response
    
    agent = GeminiAgent()
    agent.client = mock_client
    
    result = agent.execute_batch([{"ticker": "000660"}])
    assert "analyses" in result
    assert result["analyses"][0]["ticker"] == "000660"

def test_gemini_parse_markdown_generic_wrapper(monkeypatch):
    monkeypatch.setenv("USE_MOCK_AI", "false")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_key")
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '```\n{"analyses": [{"ticker": "035420"}], "selected_candidates": [{"ticker": "035420"}]}\n```'
    mock_client.models.generate_content.return_value = mock_response
    
    agent = GeminiAgent()
    agent.client = mock_client
    
    result = agent.execute_batch([{"ticker": "035420"}])
    assert "analyses" in result
    assert result["analyses"][0]["ticker"] == "035420"

def test_gemini_parse_invalid_json(monkeypatch):
    monkeypatch.setenv("USE_MOCK_AI", "false")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_key")
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = 'NOT A JSON RESPONSE'
    mock_client.models.generate_content.return_value = mock_response
    
    agent = GeminiAgent()
    agent.client = mock_client
    
    result = agent.execute_batch([{"ticker": "005930"}])
    # Should handle error gracefully and return empty analyses
    assert result == {"analyses": [], "selected_candidates": []}
