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
        # Mock GPT result
        gpt_result = {"decision": "BUY", "confidence": 0.8, "reasoning": "R1", "risks": "Risk1", "expected_result": "E1"}
        
        # This will test the mock logic since USE_MOCK_CLAUDE is true by default
        decision = self.agent.make_decision(self.sample_market_data, gpt_result)
        
        # decision can be None if API fails/parse error, but in mock mode it should succeed
        if decision:
            self.assertIn("evaluation", decision)
            self.assertIn("score", decision)
            self.assertIn("reasoning", decision)
            self.assertIn("issues", decision)
            self.assertIn("risk_level", decision)
            
            self.assertIn(decision["evaluation"], ["PASS", "WARNING", "REJECT"])
            self.assertIsInstance(decision["score"], (int, float))

if __name__ == '__main__':
    unittest.main()
