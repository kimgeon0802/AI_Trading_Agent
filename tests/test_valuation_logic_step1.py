import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from runtime.tool_manager.portfolio_manager import PortfolioManager

class MockDB:
    def __init__(self, cash, holdings):
        self.portfolio = {"cash": cash, "total_asset": 0}
        self.holdings = holdings
        
    def get_portfolio(self): return self.portfolio
    def get_holdings(self): return self.holdings
    def update_portfolio(self, cash, total_asset, timestamp): 
        self.portfolio = {"cash": cash, "total_asset": total_asset, "timestamp": timestamp}

# Mocking MarketDataCollector return
def create_mock_market_df(prices):
    data = [{"ticker": ticker, "close": price} for ticker, price in prices.items()]
    return pd.DataFrame(data)

def test_valuation_logic_complex():
    # Setup
    cash = 6784000
    holdings = [
        {"ticker": "T1", "quantity": 21200, "average_price": 100},
        {"ticker": "T2", "quantity": 8480, "average_price": 200}
    ]
    db = MockDB(cash, holdings)
    pm = PortfolioManager(db)
    
    # Mock prices
    prices = {"T1": 100.0, "T2": 200.0}
    mock_df = create_mock_market_df(prices)
    
    # Patch MarketDataCollector
    with patch('market.market_data_collector.MarketDataCollector') as MockCollector:
        instance = MockCollector.return_value
        instance.collect_all_markets.return_value = mock_df
        
        # Calculate
        timestamp = "2026-09-14T00:00:00"
        pm._update_total_asset(timestamp)
        
    # Verify
    state = db.get_portfolio()
    # 6,784,000 + (21,200 * 100) + (8,480 * 200) = 6,784,000 + 2,120,000 + 1,696,000 = 10,600,000
    assert state["total_asset"] == 10600000
    assert instance.collect_all_markets.call_count == 2 # Called once for each holding

def test_price_missing():
    cash = 6784000
    holdings = [
        {"ticker": "T1", "quantity": 21200, "average_price": 100},
        {"ticker": "T2", "quantity": 8480, "average_price": 200}
    ]
    db = MockDB(cash, holdings)
    pm = PortfolioManager(db)
    
    # Mock prices: T2 missing
    prices = {"T1": 100.0}
    mock_df = create_mock_market_df(prices)
    
    with patch('market.market_data_collector.MarketDataCollector') as MockCollector:
        instance = MockCollector.return_value
        instance.collect_all_markets.return_value = mock_df
        
        timestamp = "2026-09-14T00:00:00"
        # Should return None/None inside _update_total_asset and stop
        pm._update_total_asset(timestamp)
        
    # Check that portfolio wasn't updated with a wrong value
    # In my implementation, it returns early.
    assert db.portfolio["total_asset"] == 0 
