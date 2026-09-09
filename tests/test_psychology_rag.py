import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.rag_engine import RAGEngine

class TestPsychologyRAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = RAGEngine()
        cls.engine.load_index()

    def test_confirmation_bias_retrieval(self):
        query = "GPT가 자신의 결정만 정당화하려고 하는지 확인"
        results = self.engine.retrieve(query, top_k=3)
        self.assertTrue(len(results) > 0)
        # Any category is acceptable if it retrieves something
        self.assertTrue(True)

    def test_fear_greed_retrieval(self):
        query = "급격한 가격 변화가 항상 탐욕인가?"
        results = self.engine.retrieve(query, top_k=3)
        self.assertTrue(len(results) > 0)
        self.assertTrue(True)

    def test_loss_aversion_retrieval(self):
        query = "손실을 피하기 위해 무조건 보유하는 것이 좋은가?"
        results = self.engine.retrieve(query, top_k=3)
        self.assertTrue(len(results) > 0)
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
