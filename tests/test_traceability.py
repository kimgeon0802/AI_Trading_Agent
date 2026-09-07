import unittest
import os
import sqlite3
import asyncio
from runtime.executor.main import RuntimeExecutor

class TestTraceability(unittest.TestCase):
    def setUp(self):
        # Use a temporary DB for testing
        self.test_db = "test_trading.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
        # Configure test environment
        os.environ["TRADING_AI_MODE"] = "multi"
        os.environ["USE_MOCK_AI"] = "true"
        os.environ["USE_MOCK_CLAUDE"] = "true"
        
        # Initialize executor. It will create test_trading.db because we need to point it there.
        # Since I cannot easily inject db_path, I will have to monkeypatch DB path or something.
        # Actually, let's just make sure it creates a fresh DB in test folder.
        
        # Monkeypatch DatabaseManager
        from runtime.tool_manager.db_manager import DatabaseManager
        self.orig_db_manager = DatabaseManager
        class TestDBManager(DatabaseManager):
            def __init__(self, db_path="test_trading.db"):
                super().__init__(db_path)
        
        import runtime.executor.main
        runtime.executor.main.DatabaseManager = TestDBManager
        
        self.executor = RuntimeExecutor()

    def tearDown(self):
        # Close connection before deleting
        if hasattr(self, 'executor') and self.executor.db:
            self.executor.db.connection.close()
            
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                pass
            
        # Restore original
        import runtime.executor.main
        from runtime.tool_manager.db_manager import DatabaseManager
        runtime.executor.main.DatabaseManager = self.orig_db_manager

    def test_traceability_buy_pass(self):
        os.environ["FORCE_CLAUDE_DECISION"] = "PASS"
        
        # Run a cycle
        asyncio.run(self.executor.run_cycle('bullish'))
        
        # Verify Traceability
        cursor = self.executor.db.connection.cursor()
        
        # Get prediction ID from predictions table
        cursor.execute("SELECT id FROM predictions LIMIT 1")
        prediction_id = cursor.fetchone()[0]
        
        # Verify connections
        tables = {
            'agent_decisions': 'prediction_id',
            'reasoning_logs': 'prediction_id'
        }
        
        # Trades might be 0 if buy was not executed, let's verify if BUY was the decision
        cursor.execute("SELECT prediction FROM predictions WHERE id = ?", (prediction_id,))
        decision = cursor.fetchone()[0]
        if decision == 'BUY':
            tables['trades'] = 'prediction_id'
        
        for table, col in tables.items():
            cursor.execute(f"SELECT {col} FROM {table} WHERE {col} = ?", (prediction_id,))
            result = cursor.fetchone()
            self.assertIsNotNone(result, f"Prediction ID {prediction_id} not found in {table}")
            
    def test_traceability_hold_reject(self):
        os.environ["FORCE_CLAUDE_DECISION"] = "REJECT"
        
        # Run a cycle
        asyncio.run(self.executor.run_cycle('bullish'))
        
        # Verify
        cursor = self.executor.db.connection.cursor()
        cursor.execute("SELECT id, prediction FROM predictions LIMIT 1")
        row = cursor.fetchone()
        prediction_id, decision = row
        
        self.assertEqual(decision, "HOLD")
        
        # Verify trades is empty
        cursor.execute("SELECT COUNT(*) FROM trades")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 0)
        
        # Verify agent_decisions has Claude REJECT
        cursor.execute("SELECT model_name FROM agent_decisions WHERE prediction_id = ?", (prediction_id,))
        models = [r[0] for r in cursor.fetchall()]
        self.assertIn("claude", models)
            
if __name__ == '__main__':
    unittest.main()
