import pytest
from unittest.mock import MagicMock
from runtime.tool_manager.portfolio_manager import PortfolioManager

class MockDB:
    def __init__(self):
        self.portfolio = {}
        self.holdings = []
        self.trades = []
        
    def get_portfolio(self): return self.portfolio
    def get_holdings(self): return self.holdings
    def update_portfolio(self, cash, total_asset, timestamp): 
        self.portfolio = {"cash": cash, "total_asset": total_asset, "timestamp": timestamp}
    def update_holding(self, ticker, quantity, avg_price):
        for h in self.holdings:
            if h["ticker"] == ticker:
                h["quantity"] = quantity
                h["average_price"] = avg_price
                return
        self.holdings.append({"ticker": ticker, "quantity": quantity, "average_price": avg_price})
    def save_trade(self, timestamp, ticker, action, quantity, price, confidence, prediction_id=None):
        self.trades.append({"ticker": ticker, "action": action})

def test_portfolio_buy():
    db = MockDB()
    # Initialize with 10M cash
    pm = PortfolioManager(db, initial_cash=10000000)
    pm.ensure_initial_portfolio(initial_cash=10000000)
    
    ticker = "005930"
    decision = {"decision": "BUY", "confidence": 0.9}
    price = 100000
    
    pm.execute_decision(ticker, decision, price)
    
    state = pm.get_current_state()
    assert state["cash"] == 8000000 # 20% of 10M = 2M used
    assert len(state["holdings"]) == 1
    assert state["holdings"][0]["quantity"] == 20 # 2M / 100K = 20
    assert state["holdings"][0]["average_price"] == 100000

def test_portfolio_sell():
    db = MockDB()
    pm = PortfolioManager(db, initial_cash=10000000)
    pm.ensure_initial_portfolio(initial_cash=10000000)
    
    # Pre-setup holding
    db.update_holding("005930", 10, 100000)
    
    ticker = "005930"
    decision = {"decision": "SELL", "confidence": 0.9}
    price = 110000
    
    pm.execute_decision(ticker, decision, price)
    
    state = pm.get_current_state()
    assert state["cash"] == 11100000 # 10M + 1.1M = 11.1M
    assert state["holdings"][0]["quantity"] == 0
