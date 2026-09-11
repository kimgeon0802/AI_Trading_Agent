import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("ClaudeParser")

class ClaudeParser:
    @staticmethod
    def parse_response(response_text: str) -> Optional[Dict[str, Any]]:
        """
        Claude 응답을 파싱하여 견고하게 JSON으로 추출하고 유효성 검증을 수행한다.
        """
        if not response_text:
            logger.error("Empty response text.")
            return None

        # 1. 시도: 전체를 JSON으로 파싱
        try:
            data = json.loads(response_text)
            if ClaudeParser._validate_schema(data):
                return data
        except json.JSONDecodeError:
            pass
            
        # 2. 시도: Fenced JSON 블록 추출
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        
        # 3. 시도: { ... } 구조 추출
        start = clean_text.find('{')
        end = clean_text.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            json_str = clean_text[start : end + 1]
            try:
                data = json.loads(json_str)
                if ClaudeParser._validate_schema(data):
                    return data
            except json.JSONDecodeError:
                pass
            
        # 4. 시도: 잘린 JSON 복구 시도 (마지막 } 추가)
        if start != -1 and end == -1:
            json_str = clean_text[start:] + '}'
            try:
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
