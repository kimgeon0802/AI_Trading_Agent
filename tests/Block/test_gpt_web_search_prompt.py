import pytest
from agents.gpt_agent.agent import GPTAgent
from runtime.tool_manager.web_search_client import SearchResult

def test_formatter_basic():
    agent = GPTAgent()
    results = [
        SearchResult(query="test", category="news", title="Title 1", snippet="Snippet 1")
    ]
    context = agent._format_web_search_context(results)
    assert "[Web Search Context]" in context
    assert "Category: news" in context
    assert "Title: Title 1" in context
    assert "Snippet: Snippet 1" in context

def test_formatter_empty():
    agent = GPTAgent()
    context = agent._format_web_search_context([])
    assert context == ""

def test_formatter_missing_fields():
    agent = GPTAgent()
    # 일부 필드만 있는 경우
    results = [
        SearchResult(query="test", title="Title only")
    ]
    context = agent._format_web_search_context(results)
    assert "Title: Title only" in context
    assert "Snippet:" not in context
