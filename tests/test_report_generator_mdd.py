import pytest
from unittest.mock import MagicMock
from runtime.tool_manager.detailed_report_generator import DetailedReportGenerator

class MockDB:
    def __init__(self, portfolio_rows=None, trade_rows=None):
        self.portfolio_rows = portfolio_rows or []
        self.trade_rows = trade_rows or []

    def execute_query(self, query, params=()):
        if "FROM portfolio" in query:
            # Match query SELECT cash, total_asset, timestamp FROM portfolio WHERE total_asset > 0 ORDER BY timestamp ASC, id ASC
            if "total_asset > 0" in query:
                return [r for r in self.portfolio_rows if r[1] > 0]
            return self.portfolio_rows
        if "FROM trades" in query:
            return self.trade_rows
        return []


def test_snapshot_zero_handling():
    """0 snapshots -> INSUFFICIENT_DATA and zero returns"""
    db = MockDB(portfolio_rows=[])
    drg = DetailedReportGenerator(db)
    metrics = drg.get_portfolio_performance_metrics()

    assert metrics["status"] == "INSUFFICIENT_DATA"
    assert metrics["daily_return"] == 0.0
    assert metrics["cumulative_return"] == 0.0
    assert metrics["mdd"] == 0.0


def test_snapshot_one_handling():
    """1 snapshot -> INSUFFICIENT_DATA and zero returns"""
    db = MockDB(portfolio_rows=[(10000000.0, 10000000.0, "2026-09-14T09:00:00")])
    drg = DetailedReportGenerator(db)
    metrics = drg.get_portfolio_performance_metrics()

    assert metrics["status"] == "INSUFFICIENT_DATA"
    assert metrics["daily_return"] == 0.0
    assert metrics["cumulative_return"] == 0.0
    assert metrics["mdd"] == 0.0


def test_ignore_intermediate_zero_total_asset_snapshots():
    """total_asset == 0 temporary snapshots during PortfolioManager BUY/SELL must be excluded"""
    # 10M initial, then intermediate row with total_asset=0 (BUY execution), then 11M final total_asset
    rows = [
        (10000000.0, 10000000.0, "2026-09-14T09:00:00"),
        (8000000.0, 0.0, "2026-09-14T09:01:00"),  # Intermediate snapshot from PortfolioManager
        (8000000.0, 11000000.0, "2026-09-14T09:02:00")
    ]
    db = MockDB(portfolio_rows=rows)
    drg = DetailedReportGenerator(db)
    metrics = drg.get_portfolio_performance_metrics()

    assert metrics["status"] == "SUCCESS"
    assert metrics["cumulative_return"] == pytest.approx(10.0)  # +10% return, NOT -100% drawdown!
    assert metrics["mdd"] == 0.0


def test_deposit_does_not_artificially_boost_returns():
    """AccountManager.deposit() should not artificially boost returns or daily returns"""
    rows = [
        (10000000.0, 10000000.0, "2026-09-14T09:00:00"),
        (15000000.0, 15000000.0, "2026-09-14T10:00:00")  # 5M deposit (cash +5M, total_asset +5M, no trade)
    ]
    db = MockDB(portfolio_rows=rows, trade_rows=[])
    drg = DetailedReportGenerator(db)
    metrics = drg.get_portfolio_performance_metrics()

    assert metrics["status"] == "SUCCESS"
    assert metrics["cumulative_return"] == 0.0
    assert metrics["daily_return"] == 0.0
    assert metrics["mdd"] == 0.0


def test_withdraw_does_not_artificially_worsen_returns_or_mdd():
    """AccountManager.withdraw() should not artificially cause negative return or MDD"""
    rows = [
        (10000000.0, 10000000.0, "2026-09-14T09:00:00"),
        (7000000.0, 7000000.0, "2026-09-14T10:00:00")  # 3M withdrawal (cash -3M, total_asset -3M, no trade)
    ]
    db = MockDB(portfolio_rows=rows, trade_rows=[])
    drg = DetailedReportGenerator(db)
    metrics = drg.get_portfolio_performance_metrics()

    assert metrics["status"] == "SUCCESS"
    assert metrics["cumulative_return"] == 0.0
    assert metrics["mdd"] == 0.0


def test_normal_return_and_mdd_calculation():
    """Verify standard asset growth and drawdown calculations"""
    # 10M -> 12M (+20%) -> 9M (-25% from peak 12M) -> 11M
    # Cash stays at 5M, total_asset changes as stock market price changes
    rows = [
        (5000000.0, 10000000.0, "2026-09-14T09:00:00"),
        (5000000.0, 12000000.0, "2026-09-15T09:00:00"),
        (5000000.0, 9000000.0, "2026-09-16T09:00:00"),
        (5000000.0, 11000000.0, "2026-09-17T09:00:00")
    ]
    db = MockDB(portfolio_rows=rows)
    drg = DetailedReportGenerator(db)
    metrics = drg.get_portfolio_performance_metrics()

    # Peak index I_k reaches 1.20 at step 2.
    # Step 3 drops to 0.90 (0.90 / 1.20 = 0.75, drawdown = 25%).
    # Step 4 rises to 1.10 (Cumulative return +10%).
    assert metrics["status"] == "SUCCESS"
    assert metrics["cumulative_return"] == pytest.approx(10.0)
    assert metrics["mdd"] == pytest.approx(25.0)


def test_zero_asset_or_peak_handles_without_error():
    """Initial asset or zero values should be guarded against ZeroDivisionError"""
    rows = [
        (0.0, 0.0, "2026-09-14T09:00:00"),  # total_asset = 0.0 filtered out by query WHERE total_asset > 0
        (1000000.0, 1000000.0, "2026-09-14T10:00:00")
    ]
    db = MockDB(portfolio_rows=rows)
    drg = DetailedReportGenerator(db)
    metrics = drg.get_portfolio_performance_metrics()

    assert metrics["daily_return"] == 0.0
    assert metrics["cumulative_return"] == 0.0
    assert metrics["mdd"] == 0.0
