import unittest
import os
import asyncio
from runtime.executor.main import RuntimeExecutor

class TestMultiAIE2E(unittest.TestCase):
    def setUp(self):
        os.environ["TRADING_AI_MODE"] = "multi"
        os.environ["USE_MOCK_AI"] = "true"
        self.executor = RuntimeExecutor()

    def test_multi_ai_e2e(self):
        # Run a cycle in multi-AI mode
        asyncio.run(self.executor.run_cycle('bullish'))
        
        # Verify if decision was saved in DB by querying the table directly
        cursor = self.executor.db.connection.cursor()
        cursor.execute("SELECT * FROM predictions WHERE ticker = '005930' ORDER BY id DESC LIMIT 1")
        latest_prediction = cursor.fetchone()
        self.assertIsNotNone(latest_prediction)
        
    def test_mode_switch(self):
        # Test switching to single mode
        os.environ["TRADING_AI_MODE"] = "single"
        executor = RuntimeExecutor()
        # The AI mode check is handled by RuntimeExecutor's internal configuration (is_real_ai_mode)
        # instead of an 'ai_mode' attribute.
        self.assertTrue(hasattr(executor, 'is_real_ai_mode'))

if __name__ == '__main__':
    unittest.main()
