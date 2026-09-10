import os
import pytest
from agents.gpt_agent.agent import GPTAgent
from runtime.tool_manager.query_builder import QueryBuilder
from runtime.tool_manager.web_search_client import WebSearchClient
from runtime.tool_manager.api_error_handler import APIStatus
from unittest.mock import MagicMock

def test_gpt_web_search_integration():
    # 1. Setup
    os.environ["USE_MOCK_AI"] = "true"
    
    # Mock GPTAgent.client.get_completion to avoid calling API
    agent = GPTAgent()
    agent.client.get_completion = MagicMock(return_value=(APIStatus.SUCCESS, '{"decision": "BUY", "confidence": 0.8, "reasoning": "Mock reasoning", "risks": "Mock risks", "expected_result": "Mock result"}'))
    
    builder = QueryBuilder()
    client = WebSearchClient()
    
    market_data = {"name": "SK하이닉스", "sector": "반도체"}
    
    # 2. Pipeline
    queries = builder.build_queries(market_data)
    all_results = []
    for q in queries:
        status, results = client.search(q["query"], q["category"])
        if status == APIStatus.SUCCESS:
            all_results.extend(results)
    
    # 3. GPT Agent
    decision = agent.make_decision(market_data, web_search_results=all_results)
    
    # 4. Verify
    assert decision is not None
    assert decision["decision"] == "BUY"
    
    # Verify GPT was called with web search context in user_prompt
    args, kwargs = agent.client.get_completion.call_args
    user_prompt = args[1]
    assert "[Web Search Context]" in user_prompt
    assert "Mock Title for" in user_prompt
