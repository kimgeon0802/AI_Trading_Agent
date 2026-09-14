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

        # 1. Markdown code block 내부의 텍스트가 있다면 우선 추출
        candidate_text = response_text
        block_match = re.search(r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL)
        if block_match:
            candidate_text = block_match.group(1)

        # 2. candidate_text에서 가장 바깥쪽 { 와 } 위치 탐색 및 파싱
        start = candidate_text.find('{')
        end = candidate_text.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_str = candidate_text[start : end + 1]
            try:
                data = json.loads(json_str, strict=False)
                if ClaudeParser._validate_schema(data):
                    return data
            except json.JSONDecodeError:
                pass

        # 3. candidate_text에서 파싱 실패 시, 전체 response_text에서 가장 바깥쪽 { 와 } 탐색
        if candidate_text != response_text:
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = response_text[start : end + 1]
                try:
                    data = json.loads(json_str, strict=False)
                    if ClaudeParser._validate_schema(data):
                        return data
                except json.JSONDecodeError:
                    pass

        # 4. 전체 텍스트 직접 json.loads 시도
        try:
            data = json.loads(response_text.strip(), strict=False)
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
