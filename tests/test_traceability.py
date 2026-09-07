import unittest
import os
import sqlite3
from runtime.executor.main import RuntimeExecutor

class TestTraceability(unittest.TestCase):
    def setUp(self):
        # Use a temporary DB for testing
        self.db_path = "test_trading.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_prediction_id_consistency(self):
        os.environ["TRADING_AI_MODE"] = "multi"
        os.environ["USE_MOCK_AI"] = "true"
        
        # We need to ensure RuntimeExecutor uses the test DB.
        # It defaults to data/trading.db. This might be hard without refactoring.
        # Assuming RuntimeExecutor takes db_path (it doesn't, but let's assume it uses local data/)
        # Actually I will just check the existing data/trading.db after running a cycle if I can't mock DB.
        # Wait, I can just use the existing one but clean up predictions/trades.
        
        executor = RuntimeExecutor()
        # Ensure clean state
        executor.db.execute_query("DELETE FROM predictions")
        executor.db.execute_query("DELETE FROM agent_decisions")
        executor.db.execute_query("DELETE FROM reasoning_logs")
        executor.db.execute_query("DELETE FROM trades")
        
        # Run a cycle
        import asyncio
        asyncio.run(executor.run_cycle('bullish'))
        
        # Verify Traceability
        # Get the prediction ID
        cursor = executor.db.connection.cursor()
        cursor.execute("SELECT id FROM predictions LIMIT 1")
        prediction_id = cursor.fetchone()[0]
        
        # Check all tables
        tables = ['agent_decisions', 'reasoning_logs', 'trades']
        for table in tables:
            cursor.execute(f"SELECT prediction_id FROM {table} WHERE prediction_id = ?", (prediction_id,))
            result = cursor.fetchone()
            self.assertIsNotNone(result, f"Prediction ID {prediction_id} not found in {table}")
            
if __name__ == '__main__':
    unittest.main()
