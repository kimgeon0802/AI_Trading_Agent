import asyncio
import os
import pandas as pd
from unittest.mock import MagicMock, patch
from runtime.executor.main import RuntimeExecutor

class MockDB:
    def save_prediction(self, *args, **kwargs): return 1
    def save_reasoning(self, *args, **kwargs): pass
    def get_portfolio(self): return {"cash": 10000000, "total_asset": 10000000}
    def get_holdings(self): return []
    def update_portfolio(self, *args, **kwargs): pass
    def update_holding(self, *args, **kwargs): pass
    def save_trade(self, *args, **kwargs): pass

def test_gemini_pipeline_mock():
    os.environ["USE_MOCK_AI"] = "true"
    
    with patch('runtime.executor.main.MultiAIOrchestrator', autospec=True) as MockOrchestrator:
        # MockExecutor setup
        executor = RuntimeExecutor()
        executor.db = MockDB()
        # Mocking the pipeline to return some candidates
        executor.market_pipeline.run = MagicMock(return_value=pd.DataFrame({
            "ticker": ["T1", "T2"],
            "name": ["Name1", "Name2"],
            "close": [100.0, 200.0]
        }))
        
        # Setup orchestrator mock
        mock_agent = MockOrchestrator.return_value
        mock_agent.execute.return_value = {
            "decision": "BUY",
            "confidence": 0.8,
            "reasoning": "Mock",
            "risks": "Mock",
            "expected_result": "Mock"
        }
        executor.agent = mock_agent
        
        # Run mock cycle
        asyncio.run(executor._run_mock_cycle())
        
        # Verify execution
        # 1. Pipeline run (Mock)
        assert executor.market_pipeline.run.called
        
        # 2. Agent execution called
        assert executor.agent.execute.called
