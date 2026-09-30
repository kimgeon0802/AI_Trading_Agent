import pytest
from agents.claude_agent.agent import ClaudeAgent
from runtime.tool_manager.web_search_client import SearchResult

def test_format_summary_normal():
    agent = ClaudeAgent()
    snippet = "Samsung Electronics announced strong earnings today. Revenue increased by 20% compared to last year. Operating profit also exceeded expectations."
    summary = agent._format_summary(snippet)
    assert "strong earnings today" in summary
    assert len(summary) <= 450

def test_format_summary_long_sentence_boundary():
    agent = ClaudeAgent()
    # Create a long snippet with multiple sentences
    sentences = [f"This is sentence number {i} with some financial details." for i in range(30)]
    snippet = " ".join(sentences)
    summary = agent._format_summary(snippet)
    assert len(summary) <= 450
    # Should end cleanly around a sentence boundary or space
    assert summary.endswith(".") or summary.endswith("...") or summary.endswith("요.") or summary.endswith("다.")

def test_format_summary_empty():
    agent = ClaudeAgent()
    assert agent._format_summary(None) == "No content summary available."
    assert agent._format_summary("") == "No content summary available."
    assert agent._format_summary("   ") == "No content summary available."

def test_make_decision_search_context_formatting():
    agent = ClaudeAgent()
    
    # Mock search results (3 items)
    r1 = SearchResult(query="test", title="News Title 1", url="https://example.com/1", snippet="This is snippet 1 about earnings. It has multiple sentences. End of sentence one.")
    r2 = SearchResult(query="test", title="News Title 2", url="https://example.com/2", snippet="This is snippet 2 about growth.")
    r3 = SearchResult(query="test", title="News Title 3", url="https://example.com/3", snippet=None)
    
    # We want to test how search_context is built in make_decision or inspect the prompt.
    # Since make_decision calls AnthropicClient (which might be mocked or real depending on USE_MOCK_AI),
    # let's inspect how search_context is constructed or patch AnthropicClient.
    
    class MockAnthropicResponse:
        def __init__(self, text):
            self.content = [type('obj', (object,), {'text': text})]
            self.stop_reason = "end_turn"

    class MockAnthropicClient:
        def get_completion(self, system_prompt, user_prompt):
            self.last_user_prompt = user_prompt
            return type('obj', (object,), {'value': 'SUCCESS'}), MockAnthropicResponse('{"evaluation": "PASS", "score": 90, "reasoning": "Good", "issues": [], "risk_level": "LOW"}')

    agent.client = MockAnthropicClient()
    
    market_data = {"ticker": "005930", "name": "Samsung Electronics"}
    gpt_result = {"decision": "BUY", "confidence": 0.9}
    
    res = agent.make_decision(market_data, gpt_result, search_results=[r1, r2, r3])
    
    prompt = agent.client.last_user_prompt
    
    assert "[Web Search Results (News & Insights)]" in prompt
    assert "Title: News Title 1" in prompt
    assert "Summary: This is snippet 1 about earnings." in prompt
    assert "URL: https://example.com/1" in prompt
    assert "Title: News Title 2" in prompt
    assert "Title: News Title 3" in prompt
    assert "Summary: No content summary available." in prompt # r3 has None snippet

def test_make_decision_empty_search_results():
    agent = ClaudeAgent()
    
    class MockAnthropicResponse:
        def __init__(self, text):
            self.content = [type('obj', (object,), {'text': text})]
            self.stop_reason = "end_turn"

    class MockAnthropicClient:
        def get_completion(self, system_prompt, user_prompt):
            self.last_user_prompt = user_prompt
            return type('obj', (object,), {'value': 'SUCCESS'}), MockAnthropicResponse('{"evaluation": "PASS", "score": 90, "reasoning": "Good", "issues": [], "risk_level": "LOW"}')

    agent.client = MockAnthropicClient()
    
    market_data = {"ticker": "005930", "name": "Samsung Electronics"}
    gpt_result = {"decision": "BUY", "confidence": 0.9}
    
    agent.make_decision(market_data, gpt_result, search_results=[])
    
    prompt = agent.client.last_user_prompt
    assert "No web search results available." in prompt
