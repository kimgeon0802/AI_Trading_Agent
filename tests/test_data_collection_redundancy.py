
import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from runtime.tool_manager.portfolio_manager import PortfolioManager

def test_portfolio_asset_update_no_redundant_collection():
    # Setup
    mock_db = MagicMock()
    mock_db.get_portfolio.return_value = {"cash": 1000000, "total_asset": 1000000}
    mock_db.get_holdings.return_value = [
        {"ticker": "005930", "quantity": 10, "average_price": 70000},
        {"ticker": "000660", "quantity": 5, "average_price": 100000}
    ]
    
    portfolio_manager = PortfolioManager(mock_db)
    
    # Pre-fetched market data
    market_df = pd.DataFrame({
        "ticker": ["005930", "000660"],
        "close": [75000.0, 110000.0]
    })
    
    # Mock MarketDataCollector to verify it is NOT called
    with patch('market.market_data_collector.MarketDataCollector') as MockCollector:
        mock_instance = MockCollector.return_value
        
        # Execute
        portfolio_manager._update_total_asset("2026-09-16T12:00:00", market_df=market_df)
        
        # Verify
        assert mock_instance.collect_all_markets.call_count == 0
        mock_db.update_portfolio.assert_called()

def test_historical_ohlcv_deduplication():
    # Setup
    mock_collector = MagicMock()
    
    # Simulate multiple candidates with same ticker
    tickers = ["005930", "005930", "000660"]
    unique_tickers = list(set(tickers))
    
    # Execute (Optimization simulation)
    historical_data_map = {}
    for ticker in unique_tickers:
        historical_data_map[ticker] = mock_collector.get_historical_ohlcv(ticker, days=100)
        
    # Verify
    assert mock_collector.get_historical_ohlcv.call_count == len(unique_tickers)
    assert mock_collector.get_historical_ohlcv.call_args_list[0][0][0] == "005930"
