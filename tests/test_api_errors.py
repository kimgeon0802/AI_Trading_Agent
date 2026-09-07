import unittest
import os
from unittest.mock import MagicMock, patch
from runtime.tool_manager.openai_client import OpenAIClient
from runtime.tool_manager.api_error_handler import APIStatus
from openai import RateLimitError, AuthenticationError, APITimeoutError

class TestOpenAIErrors(unittest.TestCase):
    def setUp(self):
        # Disable mock to test real client error handling
        with patch.dict(os.environ, {"USE_MOCK_AI": "false", "OPENAI_API_KEY": "test_key"}):
            self.client = OpenAIClient()
            self.client.client = MagicMock()

    @patch("time.sleep", return_value=None)
    def test_retryable_error(self, mock_sleep):
        # Simulate rate limit then success
        self.client.client.chat.completions.create.side_effect = [
            RateLimitError("Rate limit", response=MagicMock(), body={}),
            MagicMock(choices=[MagicMock(message=MagicMock(content='{"decision": "BUY"}'))])
        ]
        
        status, response = self.client.get_completion("sys", "user")
        self.assertEqual(status, APIStatus.SUCCESS)
        self.assertEqual(self.client.client.chat.completions.create.call_count, 2)

    @patch("time.sleep", return_value=None)
    def test_non_retryable_error(self, mock_sleep):
        # Simulate authentication error (no retry)
        self.client.client.chat.completions.create.side_effect = AuthenticationError("Auth error", response=MagicMock(), body={})
        
        status, response = self.client.get_completion("sys", "user")
        self.assertEqual(status, APIStatus.CONFIGURATION_ERROR)
        self.assertEqual(self.client.client.chat.completions.create.call_count, 1)

if __name__ == '__main__':
    unittest.main()
