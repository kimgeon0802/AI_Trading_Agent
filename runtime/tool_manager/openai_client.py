import os
import json
import random
import logging
import time
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from runtime.tool_manager.api_error_handler import APIStatus, classify_error

load_dotenv()
logger = logging.getLogger("OpenAIClient")

class OpenAIClient:
    def __init__(self):
        self.use_mock = os.getenv("USE_MOCK_AI", "false").lower() == "true"
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.max_retries = 3
        
        if not self.use_mock and not self.api_key:
            raise ValueError("OPENAI_API_KEY not found and USE_MOCK_AI is false")
        
        if not self.use_mock:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def get_completion(self, system_prompt, user_prompt):
        if self.use_mock:
            return APIStatus.SUCCESS, self._get_mock_response()
            
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                return APIStatus.SUCCESS, response.choices[0].message.content
            except OpenAIError as e:
                status = classify_error(e)
                if status == APIStatus.RETRYABLE_ERROR and attempt < self.max_retries:
                    delay = (2 ** attempt) # 1, 2, 4 seconds
                    logger.warning(f"OpenAI API retry: attempt={attempt+1}/{self.max_retries}, status={status}, delay={delay}s, error={e}")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"OpenAI API Error ({status}): {e}")
                    return status, None
            except Exception as e:
                logger.error(f"Unexpected OpenAI error: {e}")
                return APIStatus.API_ERROR, None
        return APIStatus.API_ERROR, None

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

