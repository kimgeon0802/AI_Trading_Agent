import os
import json
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    def __init__(self):
        self.use_mock = os.getenv("USE_MOCK_AI", "false").lower() == "true"
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.use_mock and not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables and USE_MOCK_AI is false")
        
        if not self.use_mock:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def get_completion(self, system_prompt, user_prompt, model="gpt-4o"):
        if self.use_mock:
            return self._get_mock_response()
            
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None

    def _get_mock_response(self):
        decisions = ["BUY", "SELL", "HOLD"]
        decision = random.choice(decisions)
        confidence = round(random.uniform(0.4, 0.9), 2)
        
        mock_data = {
            "decision": decision,
            "confidence": confidence,
            "reasoning": [
                f"Mock 분석: {decision} 결정됨",
                "기술적 지표 및 뉴스 데이터의 가상 분석 결과"
            ],
            "risks": [
                "Mock 시스템에 의한 가상 리스크 요소"
            ],
            "expected_result": "테스트 환경에서의 가상 예측 결과"
        }
        return json.dumps(mock_data, ensure_ascii=False)
