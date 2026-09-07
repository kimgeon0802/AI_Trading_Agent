import os
import json
import random
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class AnthropicClient:
    def __init__(self):
        self.use_mock = os.getenv("USE_MOCK_CLAUDE", "true").lower() == "true"
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        
        if not self.use_mock and not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found and USE_MOCK_CLAUDE is false")
        
        if not self.use_mock:
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None

    def get_completion(self, system_prompt, user_prompt):
        if self.use_mock:
            return self._get_mock_response()
            
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            # Anthropic returns content as a list of TextBlock
            return message.content[0].text
        except Exception as e:
            print(f"Error calling Anthropic API: {e}")
            return None

    def _get_mock_response(self):
        decisions = ["BUY", "SELL", "HOLD"]
        decision = random.choice(decisions)
        confidence = round(random.uniform(0.5, 0.95), 2)
        
        mock_data = {
            "decision": decision,
            "confidence": confidence,
            "reasoning": "Mock Claude 분석 결과.",
            "risks": "가상 리스크.",
            "expected_result": "테스트 환경에서의 가상 예측 결과"
        }
        return json.dumps(mock_data, ensure_ascii=False)
