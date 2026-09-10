import unittest
from agents.gemini_agent.agent import GeminiMockAgent
from agents.base_agent import BaseTradingAgent

class TestGeminiAgent(unittest.TestCase):
    def setUp(self):
        self.agent = GeminiMockAgent()
        self.sample_market_data = {
            "market_summary": {"condition": "bullish"},
            "macro_data": {},
            "portfolio": {},
            "news": [],
            "technical_indicators": {}
        }

    def test_inheritance(self):
        self.assertIsInstance(self.agent, BaseTradingAgent)

    def test_make_decision(self):
        decision = self.agent.make_decision(self.sample_market_data)
        
        self.assertIn("decision", decision)
        self.assertIn("confidence", decision)
        self.assertIn("reasoning", decision)
        self.assertIn("risks", decision)
        self.assertIn("expected_result", decision)
        
        self.assertIn(decision["decision"], ["BUY", "SELL", "HOLD"])
        self.assertIsInstance(decision["confidence"], float)

    def test_bullish_logic(self):
        data = {"market_summary": {"condition": "bullish"}}
        decision = self.agent.make_decision(data)
        self.assertEqual(decision["decision"], "BUY")

    def test_bearish_logic(self):
        data = {"market_summary": {"condition": "bearish"}}
        decision = self.agent.make_decision(data)
        self.assertEqual(decision["decision"], "SELL")

if __name__ == '__main__':
    unittest.main()
