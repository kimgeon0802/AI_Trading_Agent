import json
import pytest
from agents.gemini_agent.agent import GeminiAgent
from runtime.tool_manager.tavily_search_provider import TavilySearchProvider
from agents.claude_agent.agent import ClaudeAgent
from runtime.tool_manager.consensus_engine import ConsensusEngine
from unittest.mock import MagicMock

def test_pipeline_integration_mock_e2e():
    # 1. Setup Mock Agents
    gemini = GeminiAgent()
    gemini.make_decision = MagicMock(return_value={
        "decision": "BUY",
        "confidence": 0.8,
        "selected_candidates": [{"ticker": "005930", "priority": "HIGH"}]
    })
    
    tavily = TavilySearchProvider()
    tavily.search = MagicMock(return_value=("SUCCESS", [MagicMock(title="News", url="http://n.com", snippet="Content")]))
    
    claude = ClaudeAgent()
    claude.make_decision = MagicMock(return_value={
        "evaluation": "PASS",
        "score": 85,
        "reasoning": "Reasoning",
        "issues": [],
        "risk_level": "LOW"
    })
    
    # 2. Pipeline Execution
    gemini_result = gemini.make_decision([{"ticker": "005930"}])
    candidates = gemini_result.get("selected_candidates", [])
    
    tavily_news = {}
    for candidate in candidates:
        _, news = tavily.search(f"{candidate['ticker']} 뉴스", category="news")
        tavily_news[candidate['ticker']] = [{"title": n.title, "url": n.url, "content": n.snippet} for n in news]
        
    claude_result = claude.make_decision(
        market_data={"ticker": "005930"},
        gpt_result=gemini_result,
        search_results=None 
    )
    
    consensus_result = ConsensusEngine.analyze(gemini_result, claude_result)
    
    # 3. Assertions
    assert consensus_result["status"] == "AGREEMENT"
    assert consensus_result["decision"] == "BUY"
    print("\nMock E2E Pipeline Passed.")
    print(json.dumps(consensus_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_pipeline_integration_mock_e2e()
