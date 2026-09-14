import pytest
from unittest.mock import MagicMock, patch
from runtime.tool_manager.detailed_report_generator import DetailedReportGenerator

class MockDBForCycleFilter:
    def __init__(self, trades):
        # trades: list of tuples (id, prediction_id, timestamp, ticker, decision, price, quantity)
        self.trades = trades

    def get_portfolio(self):
        return {"cash": 10000000.0, "total_asset": 10000000.0}

    def get_holdings(self):
        return []

    def execute_query(self, query, params=()):
        if "FROM portfolio" in query:
            return [(10000000.0,)]
        if "DISTINCT ticker FROM trades" in query:
            if "prediction_id IN" in query:
                # Extract placeholders matching params
                pred_ids = params if not isinstance(params[0], tuple) else params[0]
                filtered = [t for t in self.trades if t[1] in pred_ids]
                unique_tickers = list(set(t[3] for t in filtered))
                return [(t,) for t in unique_tickers]
            else:
                unique_tickers = list(set(t[3] for t in self.trades))
                return [(t,) for t in unique_tickers]

        if "SELECT decision, quantity, price FROM trades" in query:
            ticker = params[0]
            if "prediction_id IN" in query:
                pred_ids = params[1:]
                filtered = [t for t in self.trades if t[3] == ticker and t[1] in pred_ids]
            else:
                filtered = [t for t in self.trades if t[3] == ticker]
            return [(t[4], t[6], t[5]) for t in filtered]

        if "SELECT COUNT(*), SUM(quantity)" in query:
            ticker = params[0]
            if "BUY" in query:
                decision = 'BUY'
            else:
                decision = 'SELL'

            if "prediction_id IN" in query:
                pred_ids = params[1:]
                filtered = [t for t in self.trades if t[3] == ticker and t[4] == decision and t[1] in pred_ids]
            else:
                filtered = [t for t in self.trades if t[3] == ticker and t[4] == decision]

            count = len(filtered)
            qty_sum = sum(t[6] for t in filtered) if count > 0 else 0
            val_sum = sum(t[6] * t[5] for t in filtered) if count > 0 else 0
            return [(count, qty_sum, val_sum)]

        if "SELECT id, prediction_id, timestamp, ticker, decision, price, quantity FROM trades" in query:
            if "prediction_id IN" in query:
                pred_ids = params
                filtered = [t for t in self.trades if t[1] in pred_ids]
            else:
                filtered = self.trades
            return sorted(filtered, key=lambda x: x[2], reverse=True)

        return []


def test_cycle_filtering_single_prediction_id():
    """Test 1: Only trades belonging to prediction_id=3 are included when prediction_ids=[3]"""
    # Past Cycle: pred 1 (BUY T1 10@100, SELL T1 10@150 -> Win), pred 2 (BUY T2 10@100, SELL T2 10@80 -> Loss)
    # Current Cycle: pred 3 (BUY T1 5@100, SELL T1 5@200 -> Win)
    trades = [
        (1, 1, "2026-09-14T09:00:00", "T1", "BUY", 100, 10),
        (2, 1, "2026-09-14T09:05:00", "T1", "SELL", 150, 10),
        (3, 2, "2026-09-14T10:00:00", "T2", "BUY", 100, 10),
        (4, 2, "2026-09-14T10:05:00", "T2", "SELL", 80, 10),
        (5, 3, "2026-09-14T11:00:00", "T1", "BUY", 100, 5),
        (6, 3, "2026-09-14T11:05:00", "T1", "SELL", 200, 5)
    ]
    db = MockDBForCycleFilter(trades)
    drg = DetailedReportGenerator(db)

    # When filtering by Current Cycle prediction_ids=[3]:
    stats = drg.get_trading_statistics(prediction_ids=[3])

    assert stats["total_trades"] == 1
    assert stats["winning_trades"] == 1
    assert stats["losing_trades"] == 0
    assert stats["gross_profit"] == 500  # 5 * (200 - 100)


def test_multiple_prediction_ids_filtering():
    """Test 2: Trades for predictions [1, 2, 3] are all included"""
    trades = [
        (1, 1, "2026-09-14T09:00:00", "T1", "BUY", 100, 10),
        (2, 1, "2026-09-14T09:05:00", "T1", "SELL", 150, 10),
        (3, 2, "2026-09-14T10:00:00", "T2", "BUY", 100, 10),
        (4, 2, "2026-09-14T10:05:00", "T2", "SELL", 80, 10),
        (5, 3, "2026-09-14T11:00:00", "T1", "BUY", 100, 5),
        (6, 3, "2026-09-14T11:05:00", "T1", "SELL", 200, 5),
        (7, 99, "2026-09-14T12:00:00", "T3", "BUY", 50, 10) # Out of scope
    ]
    db = MockDBForCycleFilter(trades)
    drg = DetailedReportGenerator(db)

    stats = drg.get_trading_statistics(prediction_ids=[1, 2, 3])

    assert stats["total_trades"] == 3
    assert stats["winning_trades"] == 2
    assert stats["losing_trades"] == 1


def test_none_prediction_ids_backward_compatibility():
    """Test 3: prediction_ids=None retrieves all trades across all predictions"""
    trades = [
        (1, 1, "2026-09-14T09:00:00", "T1", "BUY", 100, 10),
        (2, 1, "2026-09-14T09:05:00", "T1", "SELL", 150, 10),
        (3, 2, "2026-09-14T10:00:00", "T2", "BUY", 100, 10),
        (4, 2, "2026-09-14T10:05:00", "T2", "SELL", 80, 10)
    ]
    db = MockDBForCycleFilter(trades)
    drg = DetailedReportGenerator(db)

    stats = drg.get_trading_statistics() # prediction_ids omitted

    assert stats["total_trades"] == 2
    assert stats["winning_trades"] == 1
    assert stats["losing_trades"] == 1


def test_empty_list_prediction_ids_handling():
    """Test 4: prediction_ids=[] handles empty list safely without invalid SQL or fetching all trades"""
    trades = [
        (1, 1, "2026-09-14T09:00:00", "T1", "BUY", 100, 10),
        (2, 1, "2026-09-14T09:05:00", "T1", "SELL", 150, 10)
    ]
    db = MockDBForCycleFilter(trades)
    drg = DetailedReportGenerator(db)

    stats = drg.get_trading_statistics(prediction_ids=[])

    assert stats["total_trades"] == 0
    assert stats["winning_trades"] == 0
    assert stats["losing_trades"] == 0
    assert stats["win_rate"] == 0.0

