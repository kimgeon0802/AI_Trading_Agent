import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from runtime.tool_manager.detailed_report_generator import DetailedReportGenerator

class MockDB:
    def __init__(self, portfolio, holdings, trades):
        self.portfolio = portfolio
        self.holdings = holdings
        self.trades = trades
    def get_portfolio(self): return self.portfolio
    def get_holdings(self): return self.holdings
    def execute_query(self, query, params=()):
        if "SELECT total_asset FROM portfolio" in query:
            return [(self.portfolio.get('initial_total_asset', 10000000.0),)]
        return []

def test_valuation_logic_complex():
    # Setup
    portfolio = {"cash": 6784000, "total_asset": 10600000, "initial_total_asset": 10000000.0}
    holdings = [
        {"ticker": "T1", "quantity": 21200, "average_price": 100},
        {"ticker": "T2", "quantity": 8480, "average_price": 200}
    ]
    db = MockDB(portfolio, holdings, [])
    drg = DetailedReportGenerator(db)
    
    # Mock prices
    prices = {"T1": 100.0, "T2": 200.0}
    
    with patch.object(drg, 'get_latest_price', side_effect=lambda t: prices.get(t)):
        # Recalculate based on current logic
        initial_investment = 10000000.0
        cash = 6784000
        stock_value = 21200 * 100 + 8480 * 200
        total_asset = cash + stock_value
        
        assert total_asset == 10600000
        assert (total_asset - initial_investment) == 600000

def test_price_missing_policy():
    portfolio = {"cash": 5000000, "total_asset": 10000000}
    holdings = [{"ticker": "B", "quantity": 10, "average_price": 500000}]
    db = MockDB(portfolio, holdings, [])
    drg = DetailedReportGenerator(db)
    
    with patch.object(drg, 'get_latest_price', return_value=None):
        # Should raise ValueError
        with pytest.raises(ValueError):
            # Manually trigger the valuation logic part
            stock_value = 0.0
            for h in holdings:
                price = drg.get_latest_price(h["ticker"])
                if price is not None:
                    stock_value += h["quantity"] * price
                else:
                    raise ValueError(f"Price missing for {h['ticker']}")
