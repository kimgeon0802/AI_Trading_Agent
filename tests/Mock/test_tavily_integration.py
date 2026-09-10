import os
import pytest
from runtime.tool_manager.tavily_search_provider import TavilySearchProvider
from runtime.tool_manager.api_error_handler import APIStatus

def test_tavily_pipeline_mock():
    os.environ["USE_MOCK_AI"] = "true"
    provider = TavilySearchProvider()
    
    # 1. 시뮬레이션: 검색 호출
    query = "SK하이닉스 반도체 전망"
    status, results = provider.search(query, category="sector")
    
    # 2. 결과 검증
    assert status == APIStatus.SUCCESS
    assert len(results) > 0
    assert results[0].query == query
    assert results[0].category == "sector"
    
    # 3. 데이터 구조 검증
    result = results[0]
    assert result.title is not None
    assert result.url is not None
