import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.rag_engine import RAGEngine

class TestMacroRAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = RAGEngine()
        cls.engine.load_index()

    def test_interest_rate_retrieval(self):
        query = "How do interest rates affect equity valuations?"
        results = self.engine.retrieve(query, top_k=2)
        self.assertTrue(len(results) > 0)
        categories = [r.metadata['category'] for r in results]
        self.assertIn('macro', categories)

    def test_cpi_retrieval(self):
        query = "What is the impact of rising CPI?"
        results = self.engine.retrieve(query, top_k=2)
        self.assertTrue(len(results) > 0)
        categories = [r.metadata['category'] for r in results]
        self.assertIn('macro', categories)

    def test_exchange_rate_retrieval(self):
        query = "How does exchange rate affect exporters?"
        results = self.engine.retrieve(query, top_k=2)
        self.assertTrue(len(results) > 0)
        categories = [r.metadata['category'] for r in results]
        self.assertIn('macro', categories)

if __name__ == "__main__":
    unittest.main()
