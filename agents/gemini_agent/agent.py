import os
import json
import logging
from typing import List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from agents.base_agent import BaseTradingAgent
from runtime.tool_manager.api_error_handler import APIStatus

# 환경변수 로드
load_dotenv()

logger = logging.getLogger("GeminiAgent")

class GeminiAgent(BaseTradingAgent):
    def __init__(self, system_prompt_path="prompts/system_prompt.md", decision_prompt_path="prompts/decision_prompt.md"):
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.system_prompt = self._load_prompt(system_prompt_path)
        self.decision_prompt = self._load_prompt(decision_prompt_path)
        
        # 실제 API 호출을 방지하기 위해 테스트 환경에서는 client를 생성하지 않거나 mock으로 처리
        if not os.getenv("USE_MOCK_AI", "false").lower() == "true":
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found")
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def _load_prompt(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def make_decision(self, market_data: dict) -> dict:
        """
        Gemini 모델을 사용한 1차 투자 분석 수행.
        """
        # 1. 프롬프트 구성
        macro_data = market_data.get("macro_data", {})
        macro_str = json.dumps(macro_data, indent=2, ensure_ascii=False) if macro_data else "No current macro data available."
        
        user_prompt = self.decision_prompt.replace("{{MACRO_DATA}}", macro_str)
        user_prompt += f"\n\n# Market Data\n{json.dumps(market_data, indent=2, ensure_ascii=False)}"

        # 2. Mock 모드 처리
        if os.getenv("USE_MOCK_AI", "false").lower() == "true":
            return self._get_mock_decision(market_data)

        # 3. 실제 API 호출
        try:
            # Google Search Grounding 없이 일반 분석 수행
            config = types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                response_mime_type="application/json"
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config
            )
            
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return None

    def _get_mock_decision(self, market_data: dict) -> dict:
        return {
            "decision": "HOLD",
            "confidence": 0.5,
            "reasoning": ["Mock reasoning based on market data"],
            "risks": ["Mock risks"],
            "expected_result": "Mock outcome"
        }
