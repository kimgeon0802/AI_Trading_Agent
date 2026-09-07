import unittest
from runtime.tool_manager.db_manager import DatabaseManager
from runtime.tool_manager.macro_manager import MacroManager
import os

class TestMacroManager(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager(":memory:") # Use in-memory DB for tests
        self.macro = MacroManager(self.db)

    def test_fetch_and_save_macro_data(self):
        # Without API Key, should fall back to mock
        data = self.macro.fetch_and_save_macro_data()
        self.assertIn("exchange_rate", data)
        self.assertIn("interest_rate", data)
        
        # Verify saved in DB
        latest = self.db.get_latest_macro_data()
        self.assertEqual(latest["exchange_rate"], data["exchange_rate"])

if __name__ == '__main__':
    unittest.main()
