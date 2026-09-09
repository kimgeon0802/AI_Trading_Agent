import unittest
from unittest.mock import MagicMock, patch
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.gpt_agent.agent import GPTAgent
from runtime.tool_manager.api_error_handler import APIStatus

class TestGPTErrorHandling(unittest.TestCase):
    def setUp(self):
        self.agent = GPTAgent()

    def test_case_2_api_exception(self):
        print("\n[Running] Case 2: OpenAI Client Exception")
        with patch.object(self.agent.client, 'get_completion', return_value=(APIStatus.API_ERROR, None)):
            result = self.agent.make_decision({})
            self.assertIsNone(result)
            print("Result: PASS (Handled API Error)")

    def test_case_4_empty_response(self):
        print("\n[Running] Case 4: Empty Response")
        with patch.object(self.agent.client, 'get_completion', return_value=(APIStatus.SUCCESS, "")):
            result = self.agent.make_decision({})
            self.assertIsNone(result)
            print("Result: PASS (Handled Empty Response)")

    def test_case_5_json_parse_error(self):
        print("\n[Running] Case 5: JSON Parse Error")
        with patch.object(self.agent.client, 'get_completion', return_value=(APIStatus.SUCCESS, "{invalid json}")):
            result = self.agent.make_decision({})
            self.assertIsNone(result)
            print("Result: PASS (Handled Parse Error)")

    def test_case_6_missing_fields(self):
        print("\n[Running] Case 6: Missing Required Fields")
        bad_json = json.dumps({"decision": "BUY"}) # missing other fields
        with patch.object(self.agent.client, 'get_completion', return_value=(APIStatus.SUCCESS, bad_json)):
            result = self.agent.make_decision({})
            self.assertIsNone(result)
            print("Result: PASS (Handled Missing Fields)")

    def test_case_7_invalid_data_type(self):
        print("\n[Running] Case 7: Invalid Data Type")
        bad_json = json.dumps({
            "decision": "INVALID_TYPE",
            "confidence": 0.5,
            "reasoning": [],
            "risks": [],
            "expected_result": ""
        })
        with patch.object(self.agent.client, 'get_completion', return_value=(APIStatus.SUCCESS, bad_json)):
            result = self.agent.make_decision({})
            self.assertIsNone(result)
            print("Result: PASS (Handled Invalid Decision Type)")

if __name__ == "__main__":
    unittest.main()
