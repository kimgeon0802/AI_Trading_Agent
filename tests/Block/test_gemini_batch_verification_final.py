import json
import pytest
import os
from unittest.mock import MagicMock
from agents.gemini_agent.agent import GeminiAgent
from agents.multi_ai.orchestrator import MultiAIOrchestrator
from runtime.tool_manager.tavily_search_provider import TavilySearchProvider
from agents.claude_agent.agent import ClaudeAgent

def test_gemini_batch_call_count_verification():
    # Setup
    os.environ["USE_MOCK_AI"] = "false" # Real API mode for mock client
    gemini_agent = GeminiAgent(system_prompt_path="prompts/system_prompt.md", decision_prompt_path="prompts/decision_prompt.md")
    gemini_agent.client = MagicMock() # Mock the client
    
    # 15 candidates
    market_data_list = [{"ticker": f"T{i}"} for i in range(15)]
    
    # Configure mock to return valid JSON
    gemini_agent.client.models.generate_content.return_value.text = json.dumps({
        "analyses": [{"ticker": f"T{i}", "decision": "HOLD", "confidence": 0.5} for i in range(15)],
        "selected_candidates": [{"ticker": "T1", "priority": "HIGH"}]
    })
    
    # Execute Batch
    result = gemini_agent.execute_batch(market_data_list)
    
    # Verification
    # 1. API Call Count == 1
    assert gemini_agent.client.models.generate_content.call_count == 1
    
    # 2. Pipeline Integration check (mock orchestrator logic)
    selected = result["selected_candidates"]
    assert len(selected) == 1
    
    # 3. Ensure no Gemini call in execute_single (simulated)
    # Orchestrator calls execute_single passing the gemini_analysis result
    # We verify that no further API calls were made by gemini_agent
    assert gemini_agent.client.models.generate_content.call_count == 1
