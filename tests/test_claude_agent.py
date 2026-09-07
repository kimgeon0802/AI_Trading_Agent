import unittest
from agents.claude_agent.agent import ClaudeMockAgent
from agents.base_agent import BaseTradingAgent

class TestClaudeAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ClaudeMockAgent()
        self.sample_market_data = {
            "sentiment_analysis": {"score": 0.0},
            "risk_report": {"risk_level": "medium"}
        }

    def test_inheritance(self):
        self.assertIsInstance(self.agent, BaseTradingAgent)

    def test_make_decision_structure(self):
        decision = self.agent.make_decision(self.sample_market_data)
        
        self.assertIn("decision", decision)
        self.assertIn("confidence", decision)
        self.assertIn("reasoning", decision)
        self.assertIn("risks", decision)
        self.assertIn("expected_result", decision)
        
        self.assertIn(decision["decision"], ["BUY", "SELL", "HOLD"])
        self.assertIsInstance(decision["confidence"], float)

    def test_buy_logic(self):
        # Sentiment > 0.2, Risk != high
        data = {"sentiment_analysis": {"score": 0.5}, "risk_report": {"risk_level": "low"}}
        decision = self.agent.make_decision(data)
        self.assertEqual(decision["decision"], "BUY")

    def test_sell_logic(self):
        # Sentiment < -0.2 OR Risk == high
        data = {"sentiment_analysis": {"score": -0.5}, "risk_report": {"risk_level": "low"}}
        decision = self.agent.make_decision(data)
        self.assertEqual(decision["decision"], "SELL")

if __name__ == '__main__':
    unittest.main()
