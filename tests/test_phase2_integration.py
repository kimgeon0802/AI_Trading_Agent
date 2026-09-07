import unittest
from runtime.tool_manager.db_manager import DatabaseManager
from runtime.tool_manager.macro_manager import MacroManager
from runtime.tool_manager.risk_manager import RiskManager

class TestPhase2Integration(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager(":memory:")
        self.macro = MacroManager(self.db)
        self.risk = RiskManager(self.db)
        # Mock portfolio for risk manager
        self.db.update_portfolio(10000000, 10000000, "2026-09-04T10:00:00")

    def test_full_pipeline(self):
        # 1. Macro Manager saves data
        data = self.macro.fetch_and_save_macro_data()
        
        # 2. Get data back from DB
        macro_data = self.macro.get_current_macro_indicators()
        self.assertEqual(macro_data["exchange_rate"], data["exchange_rate"])
        
        # 3. Risk Manager uses macro data
        risk_report = self.risk.get_risk_report("005930", 78000.0, macro_data=macro_data)
        self.assertIn("macro_risk_impact", risk_report)

if __name__ == '__main__':
    unittest.main()
