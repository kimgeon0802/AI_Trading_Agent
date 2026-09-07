import unittest
from agents.multi_ai.consensus_manager import ConsensusManager

class TestConsensusManager(unittest.TestCase):
    def setUp(self):
        self.gpt_buy = {"decision": "BUY", "confidence": 0.8, "reasoning": "R1", "risks": "Risk1", "expected_result": "E1"}
        self.claude_pass = {"evaluation": "PASS", "score": 90, "reasoning": "R", "issues": [], "risk_level": "LOW"}
        self.claude_reject = {"evaluation": "REJECT", "score": 20, "reasoning": "R", "issues": ["High risk"], "risk_level": "HIGH"}

    def test_agreement(self):
        consensus = ConsensusManager.get_consensus(self.gpt_buy, self.claude_pass)
        self.assertEqual(consensus["decision"], "BUY")
        self.assertEqual(consensus["method"], "validated_by_claude")

    def test_rejection(self):
        consensus = ConsensusManager.get_consensus(self.gpt_buy, self.claude_reject)
        self.assertEqual(consensus["decision"], "HOLD")
        self.assertEqual(consensus["method"], "risk_gate_rejection")

    def test_one_failure(self):
        consensus = ConsensusManager.get_consensus(self.gpt_buy, None)
        self.assertEqual(consensus["decision"], "HOLD")
        self.assertEqual(consensus["method"], "fallback_hold")

    def test_all_failures(self):
        consensus = ConsensusManager.get_consensus(None, None)
        self.assertEqual(consensus["decision"], "HOLD")
        self.assertEqual(consensus["method"], "fallback_hold")

if __name__ == '__main__':
    unittest.main()
