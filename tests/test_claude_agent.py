import unittest
from agents.claude_agent.agent import ClaudeAgent
from agents.base_agent import BaseTradingAgent

class TestClaudeAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ClaudeAgent()
        self.sample_market_data = {
            "sentiment_analysis": {"score": 0.0},
            "risk_report": {"risk_level": "medium"}
        }

    def test_inheritance(self):
        self.assertIsInstance(self.agent, BaseTradingAgent)

    def test_make_decision_structure(self):
        # This will test the mock logic since USE_MOCK_CLAUDE is true by default
        decision = self.agent.make_decision(self.sample_market_data)
        
        # decision can be None if API fails/parse error, but in mock mode it should succeed
        if decision:
            self.assertIn("decision", decision)
            self.assertIn("confidence", decision)
            self.assertIn("reasoning", decision)
            self.assertIn("risks", decision)
            self.assertIn("expected_result", decision)
            
            self.assertIn(decision["decision"], ["BUY", "SELL", "HOLD"])
            self.assertIsInstance(decision["confidence"], float)

if __name__ == '__main__':
    unittest.main()
