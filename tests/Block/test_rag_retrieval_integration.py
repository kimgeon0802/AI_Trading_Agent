import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.claude_agent.agent import ClaudeAgent

class TestRAGRetrievalIntegration(unittest.TestCase):
    def setUp(self):
        self.agent = ClaudeAgent()

    def test_rag_retrieval_flow(self):
        # Setup mock data
        market_data = {
            "name": "SK하이닉스",
            "ticker": "000660",
            "market": "KOSPI",
            "market_data": {"close": 180000, "change_rate": 3.5, "volume": 1000000},
            "screening_data": {"momentum_score": 80}
        }
        gpt_result = {
            "decision": "HOLD",
            "reasoning": "Strong trend but high volatility",
            "risks": "Market downturn"
        }
        
        # Test Retrieval
        rag_query = self.agent._build_rag_query(market_data, gpt_result)
        results = self.agent.rag_engine.retrieve(rag_query, top_k=2)
        
        # Test Context Formatting
        context = self.agent._format_rag_context(results)
        
        self.assertTrue(len(results) > 0)
        self.assertIn("[Relevant Knowledge]", context)
        self.assertIn("Source:", context)
        print(f"\n[INFO] Formatted Context:\n{context}")

if __name__ == "__main__":
    unittest.main()
