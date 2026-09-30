import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from agents.base_agent import BaseTradingAgent

# 환경변수 로드
load_dotenv()

logger = logging.getLogger("GeminiAgent")

def _log_gemini_output(data: Dict[str, Any]):
    """
    Gemini 출력을 별도 로그 파일에 기록 (비차단 방식).
    """
    try:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, "gemini_batch_output.log")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "analyses_count": len(data.get("analyses", [])),
            "selected_candidates_count": len(data.get("selected_candidates", [])),
            "analyses": data.get("analyses", []),
            "selected_candidates": data.get("selected_candidates", [])
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
    except Exception as e:
        # 로그 저장 실패가 파이프라인에 영향을 주지 않도록 경고만 남김
        logger.warning(f"Failed to log Gemini output: {e}")

class GeminiAgent(BaseTradingAgent):
    def __init__(self, system_prompt_path="prompts/system_prompt.md", decision_prompt_path="prompts/decision_prompt.md"):
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
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
        Backward compatibility: Analyze single ticker data using batch logic.
        """
        batch_result = self.execute_batch([market_data])
        analyses = batch_result.get("analyses", [])
        return analyses[0] if analyses else None

    def execute_batch(self, market_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gemini 모델을 사용한 후보군 일괄(Batch) 1차 투자 분석 수행.
        """
        if not market_data_list:
            return {"analyses": [], "selected_candidates": []}

        # 1. 프롬프트 구성
        user_prompt = self.decision_prompt.replace("{{MARKET_DATA}}", json.dumps({"candidates": market_data_list}, indent=2, ensure_ascii=False))

        # 2. Mock 모드 처리
        if os.getenv("USE_MOCK_AI", "false").lower() == "true":
            result = {
                "analyses": [self._get_single_analysis_mock(d) for d in market_data_list],
                "selected_candidates": [{"ticker": d.get("ticker"), "priority": "HIGH", "reason": "Mock reason"} for d in market_data_list[:min(len(market_data_list), 2)]]
            }
            _log_gemini_output(result)
            return result

        # 3. 실제 API 호출
        try:
            config = types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                response_mime_type="application/json",
                tools=None # AFC 비활성화
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config
            )

            # 방어적 JSON 파싱 (순수 JSON 우선 시도, 실패 시 Markdown wrapper 제거 후 재시도)
            raw_text = response.text.strip()
            try:
                data = json.loads(raw_text)
            except json.JSONDecodeError as jde:
                cleaned = raw_text
                if cleaned.startswith("```"):
                    first_newline = cleaned.find("\n")
                    if first_newline != -1:
                        cleaned = cleaned[first_newline + 1:]
                    else:
                        cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()

                if cleaned != raw_text:
                    try:
                        data = json.loads(cleaned)
                    except json.JSONDecodeError:
                        raise jde
                else:
                    raise jde

            # 파싱 후 스키마 검증
            if "analyses" not in data or "selected_candidates" not in data:
                logger.error("Gemini Batch API output missing required fields: analyses or selected_candidates.")
                return {"analyses": [], "selected_candidates": []}
            
            # 관측성 로그 기록
            _log_gemini_output(data)
            
            return data

        except Exception as e:
            error_str = str(e).lower()
            if "resource_exhausted" in error_str or "quota" in error_str:
                logger.error(f"Gemini API Quota Exceeded (429): {e}")
                return {"analyses": [], "selected_candidates": [], "error": "GEMINI_QUOTA_EXCEEDED"}
            logger.error(f"Gemini API Error: {e}")
            return {"analyses": [], "selected_candidates": []}

    def _get_single_analysis_mock(self, data: dict) -> dict:
        return {
            "ticker": data.get("ticker"),
            "decision": "BUY",
            "confidence": 0.7,
            "reasoning": "Mock reasoning",
            "risks": ["Mock risks"],
            "expected_result": "Mock outcome",
            "analysis": {
                "trend": "Up",
                "momentum": "Strong"
            }
        }
