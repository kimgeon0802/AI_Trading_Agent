import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.rag_engine import RAGEngine

class TestTechnicalRAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = RAGEngine()
        cls.engine.load_index()

    def test_volume_retrieval(self):
        query = "How to interpret trading volume?"
        results = self.engine.retrieve(query, top_k=1)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].metadata['category'], 'technical')
        self.assertIn('volume.md', results[0].metadata['source'])

    def test_moving_average_retrieval(self):
        query = "What is a moving average?"
        results = self.engine.retrieve(query, top_k=1)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].metadata['category'], 'technical')
        self.assertIn('moving_average.md', results[0].metadata['source'])

    def test_rsi_retrieval(self):
        query = "How to use RSI indicator?"
        results = self.engine.retrieve(query, top_k=1)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].metadata['category'], 'technical')
        self.assertIn('rsi.md', results[0].metadata['source'])

if __name__ == "__main__":
    unittest.main()
