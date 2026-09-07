import unittest
from unittest.mock import MagicMock
from agents.multi_ai.orchestrator import MultiAIOrchestrator

class TestMultiAIOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = MultiAIOrchestrator()
        self.sample_data = {"market_summary": {"condition": "neutral"}}
        self.mock_buy = {"decision": "BUY", "confidence": 0.8, "reasoning": "R1", "risks": "Risk1", "expected_result": "E1"}
        self.mock_sell = {"decision": "SELL", "confidence": 0.7, "reasoning": "R2", "risks": "Risk2", "expected_result": "E2"}

    def test_both_agents_success(self):
        # Mock agents
        self.orchestrator.gpt_agent.make_decision = MagicMock(return_value=self.mock_buy)
        self.orchestrator.claude_agent.make_decision = MagicMock(return_value=self.mock_buy)
        
        result = self.orchestrator.execute(self.sample_data)
        
        self.assertEqual(result["decision"], "BUY")
        self.assertIn("gpt", result["agent_results"])
        self.assertIn("claude", result["agent_results"])
        self.assertEqual(result["consensus"]["method"], "agreement")

    def test_disagreement(self):
        self.orchestrator.gpt_agent.make_decision = MagicMock(return_value=self.mock_buy)
        self.orchestrator.claude_agent.make_decision = MagicMock(return_value=self.mock_sell)
        
        result = self.orchestrator.execute(self.sample_data)
        
        # BUY (0.8) > SELL (0.7)
        self.assertEqual(result["decision"], "BUY")
        self.assertEqual(result["consensus"]["method"], "confidence_resolution")

    def test_gpt_failure(self):
        self.orchestrator.gpt_agent.make_decision = MagicMock(side_effect=Exception("API Error"))
        self.orchestrator.claude_agent.make_decision = MagicMock(return_value=self.mock_buy)
        
        result = self.orchestrator.execute(self.sample_data)
        
        self.assertEqual(result["decision"], "BUY")
        self.assertIsNone(result["agent_results"]["gpt"])
        self.assertEqual(result["agent_results"]["claude"]["decision"], "BUY")

    def test_both_failures(self):
        self.orchestrator.gpt_agent.make_decision = MagicMock(side_effect=Exception("Err"))
        self.orchestrator.claude_agent.make_decision = MagicMock(side_effect=Exception("Err"))
        
        result = self.orchestrator.execute(self.sample_data)
        
        self.assertEqual(result["decision"], "HOLD")
        self.assertEqual(result["consensus"]["method"], "fallback_hold")

if __name__ == '__main__':
    unittest.main()
