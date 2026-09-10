import pytest
from unittest.mock import MagicMock
from runtime.tool_manager.web_search_client import WebSearchClient, SearchResult
from runtime.tool_manager.api_error_handler import APIStatus
import os

def test_mock_web_search_pipeline():
    os.environ["USE_MOCK_AI"] = "true"
    client = WebSearchClient()
    
    # 가상의 검색 파이프라인 시뮬레이션
    query = "AI trading trends 2026"
    status, results = client.search(query)
    
    assert status == APIStatus.SUCCESS
    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0].query == query
    
    # 결과가 GPT 입력에 적합한 형태인지 확인 (정규화 결과 확인)
    assert isinstance(results[0], SearchResult)
    assert results[0].snippet is not None
