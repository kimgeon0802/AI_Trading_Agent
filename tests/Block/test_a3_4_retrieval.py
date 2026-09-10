import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.rag_engine import RAGEngine

class TestA3_4Retrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = RAGEngine()
        cls.engine.load_index()

    def test_fundamental_retrieval(self):
        query = "How to evaluate valuation metrics like PER?"
        results = self.engine.retrieve(query, top_k=2)
        self.assertTrue(len(results) > 0)
        categories = [r.metadata['category'] for r in results]
        self.assertIn('fundamental', categories)

    def test_investor_retrieval(self):
        query = "What is Benjamin Graham's margin of safety?"
        results = self.engine.retrieve(query, top_k=2)
        self.assertTrue(len(results) > 0)
        categories = [r.metadata['category'] for r in results]
        self.assertIn('investors', categories)

if __name__ == "__main__":
    unittest.main()
