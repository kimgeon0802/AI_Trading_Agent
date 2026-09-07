import os
import json
import random
import logging
import time
import anthropic
import httpx
from dotenv import load_dotenv
from runtime.tool_manager.api_error_handler import APIStatus, classify_error

load_dotenv()
logger = logging.getLogger("AnthropicClient")

class AnthropicClient:
    def __init__(self):
        self.use_mock = os.getenv("USE_MOCK_CLAUDE", "true").lower() == "true"
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        self.max_retries = 3
        
        if not self.use_mock and not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found and USE_MOCK_CLAUDE is false")
        
        if not self.use_mock:
            self.client = anthropic.Anthropic(api_key=self.api_key, max_retries=0)
        else:
            self.client = None

    def get_completion(self, system_prompt, user_prompt):
        if self.use_mock:
            return APIStatus.SUCCESS, self._get_mock_response()
            
        for attempt in range(self.max_retries + 1):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return APIStatus.SUCCESS, message.content[0].text
            except (anthropic.BadRequestError, anthropic.AuthenticationError) as e:
                # These are NOT retryable
                logger.error(f"Anthropic API Non-Retryable Error: {e}")
                return APIStatus.API_ERROR, None
            except anthropic.APIError as e:
                status = classify_error(e)
                if status == APIStatus.RETRYABLE_ERROR and attempt < self.max_retries:
                    delay = (2 ** attempt) # 1, 2, 4 seconds
                    logger.warning(f"Anthropic API retry: attempt={attempt+1}/{self.max_retries}, status={status}, delay={delay}s, error={e}")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Anthropic API Error ({status}): {e}")
                    return status, None
            except Exception as e:
                logger.error(f"Unexpected Anthropic error: {type(e).__name__} - {e}")
                return APIStatus.API_ERROR, None
        return APIStatus.API_ERROR, None

    def _get_mock_response(self):
        # Allow test to force a decision
        forced_decision = os.getenv("FORCE_CLAUDE_DECISION")
        if forced_decision:
            decision = forced_decision
        else:
            decisions = ["PASS", "WARNING", "REJECT"]
            decision = random.choice(decisions)
        
        score = round(random.uniform(50, 95), 2)
        
        mock_data = {
            "evaluation": decision,
            "score": score,
            "reasoning": "Mock Claude 분석 결과.",
            "issues": ["가상 리스크."],
            "risk_level": "LOW"
        }
        return json.dumps(mock_data, ensure_ascii=False)
