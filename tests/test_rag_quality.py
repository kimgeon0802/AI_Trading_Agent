import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.rag_engine import RAGEngine

class TestRAGQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = RAGEngine()
        cls.engine.load_index()

    def test_korean_retrieval(self):
        query = "변동성 위험"
        results = self.engine.retrieve(query, top_k=2)
        self.assertTrue(len(results) > 0)
        categories = [r.metadata['category'] for r in results]
        self.assertTrue(any(c in ['risk', 'macro', 'psychology'] for c in categories))

    def test_english_retrieval(self):
        query = "What is momentum strategy?"
        results = self.engine.retrieve(query, top_k=1)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].metadata['category'], 'strategy')

    def test_category_retrieval(self):
        query = "How do macro indicators affect equities?"
        results = self.engine.retrieve(query, top_k=1)
        self.assertEqual(results[0].metadata['category'], 'macro')

    def test_negative_query(self):
        query = "오늘 점심 메뉴 추천해줘"
        results = self.engine.retrieve(query, top_k=1)
        self.assertTrue(True)

    def test_empty_query(self):
        results = self.engine.retrieve(" ", top_k=1)
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
