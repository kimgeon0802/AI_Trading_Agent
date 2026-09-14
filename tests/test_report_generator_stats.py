import pytest
from unittest.mock import MagicMock, patch
from runtime.tool_manager.detailed_report_generator import DetailedReportGenerator

class MockDB:
    def __init__(self, trades):
        self.trades = trades
    def execute_query(self, query, params=()):
        if "decision = 'SELL'" in query:
            return [t for t in self.trades if t[1] == 'SELL']
        if "DISTINCT ticker" in query:
            # Correctly return DISTINCT tickers
            unique_tickers = list(set(t[0] for t in self.trades))
            return [(t,) for t in unique_tickers]
        if "decision = 'BUY'" in query:
            return [t for t in self.trades if t[1] == 'BUY' and t[0] == params[0]]
        # Mocking individual ticker trades for FIFO
        if "SELECT decision, quantity, price FROM trades WHERE ticker" in query:
            return [(t[1], t[2], t[3]) for t in self.trades if t[0] == params[0]]
        return []

def test_trading_statistics():
    # Setup: 2 tickers, mixed outcomes
    # T1: 10 @ 100 BUY, 10 @ 150 SELL (+500) -> Win
    # T2: 10 @ 100 BUY, 10 @ 80 SELL (-200) -> Loss
    trades = [
        ("T1", "BUY", 10, 100),
        ("T1", "SELL", 10, 150),
        ("T2", "BUY", 10, 100),
        ("T2", "SELL", 10, 80)
    ]
    db = MockDB(trades)
    drg = DetailedReportGenerator(db)
    
    stats = drg.get_trading_statistics()
    
    assert stats["total_trades"] == 2
    assert stats["winning_trades"] == 1
    assert stats["losing_trades"] == 1
    assert stats["win_rate"] == 50.0
    assert stats["avg_winning"] == 500
    assert stats["avg_losing"] == -200
    assert stats["profit_factor"] == 2.5 # 500 / 200

def test_partial_sell_fifo():
    # T1: BUY 10 @ 100, SELL 4 @ 150 (+200), SELL 6 @ 80 (-120). Net +80.
    trades = [
        ("T1", "BUY", 10, 100),
        ("T1", "SELL", 4, 150),
        ("T1", "SELL", 6, 80)
    ]
    db = MockDB(trades)
    drg = DetailedReportGenerator(db)
    
    stats = drg.get_trading_statistics()
    
    # SELL 1: P/L +200
    # SELL 2: P/L -120
    assert stats["winning_trades"] == 1
    assert stats["losing_trades"] == 1
    assert stats["total_trades"] == 2
