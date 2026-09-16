
import pytest
from unittest.mock import MagicMock, patch
import asyncio
from runtime.executor.main import RuntimeExecutor
from market.market_data_collector import MarketDataCollector
from runtime.tool_manager.detailed_report_generator import DetailedReportGenerator

@pytest.mark.asyncio
async def test_full_cycle_market_data_calls():
    # Setup
    with patch('market.market_data_collector.MarketDataCollector') as MockCollector:
        mock_instance = MockCollector.return_value
        # Ensure collect_all_markets returns a valid mock dataframe
        mock_instance.collect_all_markets.return_value = MagicMock()
        mock_instance.get_historical_ohlcv.return_value = MagicMock()

        # Initialize Executor
        executor = RuntimeExecutor()
        
        # We need to mock the pipeline.run to return candidates so the cycle proceeds
        executor.market_pipeline.run = MagicMock(return_value=MagicMock(empty=False))
        # Ensure refined_df is not empty
        executor.refiner.refine = MagicMock(return_value=MagicMock(empty=False))
        # Mock other dependencies that might call APIs
        executor.portfolio_manager.get_current_state = MagicMock()
        executor.macro_manager.fetch_and_save_macro_data = MagicMock()
        executor.agent.execute_batch_gemini = MagicMock(return_value={"selected_candidates": []})

        # Run Cycle (Mocking the cycle to avoid real API calls)
        await executor.run_cycle()

        # 1. Total Cycle collect_all_markets calls (Expect 1)
        # 2. Portfolio/Report calls (Expect 0)
        
        # Since we patched the class, check calls on the instance
        print(f"\n[DEBUG] Total collect_all_markets call count: {mock_instance.collect_all_markets.call_count}")
        
        # Total cycle check
        assert mock_instance.collect_all_markets.call_count == 1
        
        # Report generator check (Ensure it doesn't call it)
        db_mock = MagicMock()
        report_gen = DetailedReportGenerator(db_mock, price_map={})
        report_gen.get_latest_price("005930")
        assert mock_instance.collect_all_markets.call_count == 1 # Should still be 1
