import pytest
from unittest.mock import MagicMock
from runtime.tool_manager.tavily_search_provider import TavilySearchProvider
from runtime.tool_manager.api_error_handler import APIStatus

def test_tavily_provider_mock_search():
    # Mock 모드 강제 설정
    import os
    os.environ["USE_MOCK_AI"] = "true"
    provider = TavilySearchProvider()
    
    status, results = provider.search("test query")
    assert status == APIStatus.SUCCESS
    assert len(results) == 1
    assert results[0].query == "test query"
    assert "Mock Tavily" in results[0].title
