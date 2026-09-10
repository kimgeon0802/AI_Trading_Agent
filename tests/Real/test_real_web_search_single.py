import os
import pytest
from agents.gpt_agent.agent import GPTAgent
from runtime.tool_manager.query_builder import QueryBuilder
from runtime.tool_manager.web_search_client import WebSearchClient
from runtime.tool_manager.api_error_handler import APIStatus

@pytest.mark.skipif(os.getenv("RUN_REAL_TESTS") != "true", reason="Real tests disabled by default")
def test_real_web_search_single_stock():
    # Real 모드 활성화
    os.environ["USE_MOCK_AI"] = "false"
    
    # 0. Setup (Real Client)
    agent = GPTAgent()
    builder = QueryBuilder()
    client = WebSearchClient()
    
    # 실제 종목 데이터
    market_data = {"name": "SK하이닉스", "ticker": "000660", "sector": "반도체"}
    
    # 1. Pipeline
    queries = builder.build_queries(market_data)
    all_results = []
    
    # 실제 검색 수행
    for q in queries:
        status, results = client.search(q["query"], q["category"])
        if status == APIStatus.SUCCESS:
            all_results.extend(results)
            
    # 2. GPT Agent 분석 수행
    decision = agent.make_decision(market_data, web_search_results=all_results)
    
    # 3. Verify
    assert decision is not None
    assert "decision" in decision
    
    # 검색 결과가 하나라도 나오는지 확인 (실제 API)
    # 1종목이므로 성공적인 검색이 최소 1개는 있어야 함
    assert len(all_results) > 0
