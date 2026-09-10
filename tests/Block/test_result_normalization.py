import pytest
from unittest.mock import MagicMock
from runtime.tool_manager.web_search_client import WebSearchClient, SearchResult
from runtime.tool_manager.api_error_handler import APIStatus

def test_normalization_basic():
    client = WebSearchClient()
    
    # Mock Response 생성
    mock_response = MagicMock()
    # output 구조: item.type, item.action.sources
    item1 = MagicMock()
    item1.type = 'web_search_call'
    
    source1 = MagicMock()
    source1.url = 'https://example.com/1'
    source1.title = 'Title 1'
    
    item1.action.sources = [source1]
    
    mock_response.output = [item1]
    
    results = client._normalize_response(mock_response, "test query", "news")
    
    assert len(results) == 1
    assert results[0].url == 'https://example.com/1'
    assert results[0].category == 'news'

def test_normalization_missing_fields():
    client = WebSearchClient()
    
    mock_response = MagicMock()
    item1 = MagicMock()
    item1.type = 'web_search_call'
    
    # action.sources가 없는 경우
    item1.action = MagicMock(spec=[]) 
    
    mock_response.output = [item1]
    
    results = client._normalize_response(mock_response, "test query")
    assert len(results) == 0

def test_normalization_malformed():
    client = WebSearchClient()
    
    # output 없음
    mock_response = MagicMock(spec=[])
    
    results = client._normalize_response(mock_response, "test query")
    assert len(results) == 0
