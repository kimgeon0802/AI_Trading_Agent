import pytest
from unittest.mock import MagicMock, patch
from runtime.tool_manager.web_search_client import WebSearchClient
from runtime.tool_manager.api_error_handler import APIStatus
from openai import AuthenticationError, RateLimitError, APITimeoutError, APIConnectionError

def test_search_authentication_error():
    mock_client = MagicMock()
    mock_client.responses = MagicMock()
    mock_client.responses.create.side_effect = AuthenticationError(message="Auth failed", response=MagicMock(), body={})

    client = WebSearchClient(client=mock_client)
    client.use_mock = False

    status, results = client.search("query")
    assert status == APIStatus.CONFIGURATION_ERROR
    assert results == []

def test_search_rate_limit_error():
    mock_client = MagicMock()
    mock_client.responses = MagicMock()
    mock_client.responses.create.side_effect = RateLimitError(message="Rate limit", response=MagicMock(), body={})

    client = WebSearchClient(client=mock_client)
    client.use_mock = False

    status, results = client.search("query")
    assert status == APIStatus.RETRYABLE_ERROR
    assert results == []

def test_search_timeout_error():
    mock_client = MagicMock()
    mock_client.responses = MagicMock()
    # APITimeoutError는 일반적으로 request 인자 필요
    mock_client.responses.create.side_effect = APITimeoutError(request=MagicMock())
    
    client = WebSearchClient(client=mock_client)
    client.use_mock = False
    
    status, results = client.search("query")
    assert status == APIStatus.TIMEOUT
    assert results == []

