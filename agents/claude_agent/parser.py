import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("ClaudeParser")

class ClaudeParser:
    @staticmethod
    def parse_response(response_text: str) -> Optional[Dict[str, Any]]:
        """
        Claude 응답을 파싱하여 JSON으로 추출하고 유효성 검증을 수행합니다.
        """
        if not response_text:
            logger.error("Empty response text.")
            return None

        import re

        # 1. 시도: 정규표현식으로 { ... } 블록 추출 (가장 바깥쪽 JSON 객체 시도)
        # Markdown fence 내부에 있는 JSON을 우선적으로 찾습니다.
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                if ClaudeParser._validate_schema(data):
                    return data
            except json.JSONDecodeError:
                pass

        # 2. 시도: 전체 텍스트에서 JSON 객체 시도
        try:
            data = json.loads(response_text)
            if ClaudeParser._validate_schema(data):
                return data
        except json.JSONDecodeError:
            pass

        # 3. 시도: 더 포괄적인 { } 추출 (Markdown 내부에 있지 않은 경우 등)
        start = response_text.find('{')
        end = response_text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                json_str = response_text[start : end + 1]
                data = json.loads(json_str)
                if ClaudeParser._validate_schema(data):
                    return data
            except json.JSONDecodeError:
                pass

        logger.error(f"Failed to parse Claude response. Text: {response_text[:100]}...")
        return None

    @staticmethod
    def _validate_schema(data: Dict[str, Any]) -> bool:
        """
        필수 필드 및 타입/범위 검증
        """
        required = ["evaluation", "score", "reasoning", "issues", "risk_level"]
        
        # 필드 존재 여부
        if not all(k in data for k in required):
            logger.error("Missing required fields in Claude response.")
            return False
            
        # 타입/범위 검증
        if data["evaluation"] not in ["PASS", "WARNING", "REJECT"]:
            logger.error(f"Invalid evaluation value: {data['evaluation']}")
            return False
            
        if not isinstance(data["score"], (int, float)) or not (0 <= data["score"] <= 100):
            logger.error(f"Invalid score: {data['score']}")
            return False
            
        if not isinstance(data["issues"], list):
            logger.error("Issues must be a list.")
            return False
            
        return True
