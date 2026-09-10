import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.claude_agent.agent import ClaudeAgent

class TestRAGQueryBuilder(unittest.TestCase):
    def setUp(self):
        self.agent = ClaudeAgent()

    def test_normal_input(self):
        market_data = {
            "ticker": "000660",
            "name": "SK하이닉스",
            "market": "KOSPI",
            "market_data": {"close": 180000, "change_rate": 3.5, "volume": 1000000},
            "screening_data": {"momentum_score": 80}
        }
        gpt_result = {
            "decision": "HOLD",
            "reasoning": "Strong trend but high volatility",
            "risks": "Market downturn"
        }
        query = self.agent._build_rag_query(market_data, gpt_result)
        self.assertIn("SK하이닉스", query)
        self.assertIn("HOLD", query)
        self.assertIn("Market signals:", query)
        print(f"\n[INFO] Generated Query (Normal):\n{query}")

    def test_missing_gpt_result(self):
        market_data = {"ticker": "000660"}
        query = self.agent._build_rag_query(market_data, None)
        self.assertIn("GPT analysis: Not available", query)
        print(f"\n[INFO] Generated Query (Missing GPT):\n{query}")

    def test_long_reasoning(self):
        market_data = {"ticker": "000660"}
        gpt_result = {
            "decision": "BUY",
            "reasoning": "A" * 200,
            "risks": "B" * 200
        }
        query = self.agent._build_rag_query(market_data, gpt_result)
        self.assertTrue(len(query) < 1000) # Ensure reasonable length
        self.assertIn("A" * 25, query) # Check for truncated content
        print(f"\n[INFO] Generated Query (Long Text Truncated):\n{query}")

if __name__ == "__main__":
    unittest.main()
