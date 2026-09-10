import os
import pytest
from agents.gpt_agent.agent import GPTAgent
from runtime.tool_manager.query_builder import QueryBuilder
from runtime.tool_manager.web_search_client import WebSearchClient
from runtime.tool_manager.api_error_handler import APIStatus
from unittest.mock import MagicMock

def test_gpt_web_search_fallback():
    # Mock 모드 사용 시 성공
    os.environ["USE_MOCK_AI"] = "true"

    agent = GPTAgent()
    # Mock GPTAgent.client.get_completion
    agent.client.get_completion = MagicMock(return_value=(APIStatus.SUCCESS, '{"decision": "BUY", "confidence": 0.8, "reasoning": "Mock reasoning", "risks": "Mock risks", "expected_result": "Mock result"}'))

    # 1. Search Client를 에러가 나도록 강제 (Mock 에러 처리)
    client = WebSearchClient()
    client.search = MagicMock(return_value=(APIStatus.API_ERROR, []))

    market_data = {"name": "SK하이닉스"}

    # 2. Pipeline (Web Search 실패 상황 시뮬레이션)
    status, results = client.search("SK하이닉스 최신 뉴스")
    assert status == APIStatus.API_ERROR
    assert len(results) == 0

    # 3. GPT Agent 분석 수행 (결과가 없어도 성공해야 함)
    decision = agent.make_decision(market_data, web_search_results=results)

    # 4. Verify
    assert decision is not None
    assert decision["decision"] == "BUY"

    # Verify GPT was called WITHOUT Web Search Context (results is empty)
    args, kwargs = agent.client.get_completion.call_args
    user_prompt = args[1]
    assert "[Web Search Context]" not in user_prompt

