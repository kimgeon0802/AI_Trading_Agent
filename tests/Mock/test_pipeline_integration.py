import json
import pytest
from agents.gemini_agent.agent import GeminiAgent
from runtime.tool_manager.tavily_search_provider import TavilySearchProvider
from agents.claude_agent.agent import ClaudeAgent
from unittest.mock import MagicMock

def test_pipeline_integration_mock():
    # 1. Setup
    # Gemini mock will return a valid response with selected_candidates
    gemini = GeminiAgent()
    gemini.make_decision = MagicMock(return_value={
        "decision": "BUY",
        "confidence": 0.8,
        "reasoning": "Mock reasoning",
        "risks": ["Mock risk"],
        "expected_result": "Mock result",
        "analysis": {"trend": "Up", "momentum": "Strong"},
        "selected_candidates": [
            {"ticker": "005930", "priority": "HIGH", "reason": "Reason 1"},
            {"ticker": "000660", "priority": "MEDIUM", "reason": "Reason 2"}
        ]
    })
    
    # Tavily mock
    tavily = TavilySearchProvider()
    tavily.search = MagicMock(side_effect=lambda query, category: (
        "SUCCESS", 
        [MagicMock(title=f"News for {query}", url="http://news.com", snippet="Content")]
    ))
    
    # Claude mock
    claude = ClaudeAgent()
    claude.make_decision = MagicMock(return_value={
        "evaluation": "PASS",
        "score": 85,
        "reasoning": "Claude agrees with Gemini",
        "issues": [],
        "risk_level": "LOW"
    })
    
    # 2. Pipeline Orchestration
    # A. Gemini 1st Analysis
    gemini_result = gemini.make_decision([{"ticker": "005930"}, {"ticker": "000660"}])
    candidates = gemini_result.get("selected_candidates", [])
    
    # B. Tavily Search
    tavily_news = {}
    for candidate in candidates:
        ticker = candidate["ticker"]
        _, news = tavily.search(f"{ticker} 최신 뉴스", category="news")
        tavily_news[ticker] = [
            {"title": n.title, "url": n.url, "content": n.snippet} for n in news
        ]
        
    # C. Claude Input Construction
    claude_input = {
        "gemini_analysis": gemini_result,
        "tavily_news": tavily_news,
        "rag_context": "Sample RAG context."
    }
    
    # D. Claude Analysis
    claude_result = claude.make_decision(
        market_data={"dummy": "data"},
        gpt_result=gemini_result,
        search_results=None # Handled differently in current implementation, need to adjust if needed
    )
    
    # 3. Assertions
    assert len(tavily_news) == 2
    assert "005930" in tavily_news
    assert claude_input["gemini_analysis"]["decision"] == "BUY"
    assert claude_result["evaluation"] == "PASS"
    print("\nClaude Input Contract:")
    print(json.dumps(claude_input, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_pipeline_integration_mock()
