import json
import pytest
from agents.gemini_agent.agent import GeminiAgent
from runtime.tool_manager.tavily_search_provider import TavilySearchProvider
from agents.claude_agent.agent import ClaudeAgent
from runtime.tool_manager.consensus_engine import ConsensusEngine
from runtime.tool_manager.position_sizer import PositionSizer
from runtime.tool_manager.portfolio_manager import PortfolioManager
from unittest.mock import MagicMock

class MockDB:
    def __init__(self):
        self.portfolio = {"cash": 10000000, "total_asset": 10000000}
        self.holdings = []
    def get_portfolio(self): return self.portfolio
    def get_holdings(self): return self.holdings
    def update_portfolio(self, cash, total_asset, timestamp): 
        self.portfolio = {"cash": cash, "total_asset": total_asset}
    def update_holding(self, ticker, quantity, avg_price):
        for h in self.holdings:
            if h["ticker"] == ticker:
                h["quantity"] = quantity
                h["average_price"] = avg_price
                return
        self.holdings.append({"ticker": ticker, "quantity": quantity, "average_price": avg_price})
    def save_trade(self, *args, **kwargs): pass

def test_pipeline_full_integration_mock():
    # 1. Setup Mock Agents and Managers
    gemini = GeminiAgent()
    gemini.make_decision = MagicMock(return_value={
        "decision": "BUY",
        "confidence": 0.9,
        "selected_candidates": [{"ticker": "005930", "priority": "HIGH"}]
    })
    
    tavily = TavilySearchProvider()
    tavily.search = MagicMock(return_value=("SUCCESS", [MagicMock(title="News", url="http://n.com", snippet="Content")]))
    
    claude = ClaudeAgent()
    claude.make_decision = MagicMock(return_value={
        "evaluation": "PASS",
        "score": 90,
        "reasoning": "Reasoning",
        "issues": [],
        "risk_level": "LOW"
    })
    
    db = MockDB()
    pm = PortfolioManager(db, initial_cash=10000000)
    
    # 2. Pipeline Execution
    # Gemini
    gemini_result = gemini.make_decision([{"ticker": "005930"}])
    candidates = gemini_result.get("selected_candidates", [])
    
    # Tavily
    for candidate in candidates:
        _, news = tavily.search(f"{candidate['ticker']} 뉴스", category="news")
        
    # Claude
    claude_result = claude.make_decision(
        market_data={"ticker": "005930"},
        gpt_result=gemini_result
    )
    
    # Consensus
    consensus_result = ConsensusEngine.analyze(gemini_result, claude_result)
    
    # PositionSizer & PortfolioManager
    if consensus_result["decision"] == "BUY":
        # Simulate BUY execution
        pm.execute_decision("005930", consensus_result["gemini"], 100000)
    
    # 3. Assertions
    state = pm.get_current_state()
    assert state["cash"] < 10000000
    assert len(state["holdings"]) == 1
    assert state["holdings"][0]["ticker"] == "005930"
    print("\nFull Mock E2E Pipeline Passed.")

if __name__ == "__main__":
    test_pipeline_full_integration_mock()
