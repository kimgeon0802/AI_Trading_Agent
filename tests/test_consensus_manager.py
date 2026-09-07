import unittest
from agents.multi_ai.consensus_manager import ConsensusManager

class TestConsensusManager(unittest.TestCase):
    def setUp(self):
        self.mock_buy = {"decision": "BUY", "confidence": 0.8, "reasoning": "R1", "risks": "Risk1", "expected_result": "E1"}
        self.mock_sell = {"decision": "SELL", "confidence": 0.7, "reasoning": "R2", "risks": "Risk2", "expected_result": "E2"}

    def test_agreement(self):
        results = {"gpt": self.mock_buy, "claude": self.mock_buy}
        consensus = ConsensusManager.get_consensus(results)
        self.assertEqual(consensus["decision"], "BUY")
        self.assertEqual(consensus["consensus_type"], "agreement")

    def test_disagreement_confidence_resolution(self):
        # GPT(BUY, 0.8), Claude(SELL, 0.7) -> BUY (0.8 > 0.7)
        results = {"gpt": self.mock_buy, "claude": self.mock_sell}
        consensus = ConsensusManager.get_consensus(results)
        self.assertEqual(consensus["decision"], "BUY")
        self.assertEqual(consensus["consensus_type"], "confidence_resolution")

    def test_one_failure(self):
        results = {"gpt": self.mock_buy, "claude": None}
        consensus = ConsensusManager.get_consensus(results)
        self.assertEqual(consensus["decision"], "BUY")
        self.assertEqual(consensus["consensus_type"], "confidence_resolution")

    def test_all_failures(self):
        results = {"gpt": None, "claude": None}
        consensus = ConsensusManager.get_consensus(results)
        self.assertEqual(consensus["decision"], "HOLD")
        self.assertEqual(consensus["consensus_type"], "fallback_hold")

if __name__ == '__main__':
    unittest.main()
