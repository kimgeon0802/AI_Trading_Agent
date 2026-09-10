import os
import pytest
from runtime.tool_manager.query_builder import QueryBuilder
from runtime.tool_manager.web_search_client import WebSearchClient
from runtime.tool_manager.api_error_handler import APIStatus

def test_mock_query_builder_pipeline():
    # 1. QueryBuilder 설정
    builder = QueryBuilder()
    data = {"name": "SK하이닉스", "sector": "반도체"}
    
    # 2. Query 생성
    queries = builder.build_queries(data)
    assert len(queries) >= 3
    
    # 3. WebSearchClient 설정 (Mock 모드)
    os.environ["USE_MOCK_AI"] = "true"
    client = WebSearchClient()
    
    # 4. Pipeline 검증
    for q in queries:
        status, results = client.search(q["query"])
        assert status == APIStatus.SUCCESS
        assert len(results) > 0
        assert results[0].query == q["query"]
