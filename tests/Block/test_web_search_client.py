import pytest
from runtime.tool_manager.web_search_client import WebSearchClient
from runtime.tool_manager.api_error_handler import APIStatus
import os

def test_web_search_client_init():
    # Mock 모드 강제 설정
    os.environ["USE_MOCK_AI"] = "true"
    client = WebSearchClient()
    assert client.use_mock is True

def test_web_search_client_mock_search():
    os.environ["USE_MOCK_AI"] = "true"
    client = WebSearchClient()
    status, results = client.search("test query")
    assert status == APIStatus.SUCCESS
    assert len(results) == 1
    assert results[0].query == "test query"
    assert results[0].source == "Mock Source"

def test_web_search_client_no_key_error():
    os.environ["USE_MOCK_AI"] = "false"
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    
    with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
        WebSearchClient()
