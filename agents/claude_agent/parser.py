import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("ClaudeParser")

class ClaudeParser:
    @staticmethod
    def parse_response(response_text: str) -> Optional[Dict[str, Any]]:
        """
        Claude 응답을 파싱하여 JSON으로 추출하고 유효성 검증을 수행합니다.
        중첩 JSON과 마크다운 코드블록을 안전하게 처리합니다.
        """
        if not response_text:
            logger.error("Empty response text.")
            return None

        import json
        import re

        def try_parse(text):
            try:
                # 1. 시도: 직접 파싱
                data = json.loads(text.strip(), strict=False)
                if ClaudeParser._validate_schema(data):
                    return data
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
            return None

        # 1. 전체 텍스트 파싱 시도 (가장 최적)
        res = try_parse(response_text)
        if res: return res

        # 2. 마크다운 코드 블록 시도
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL)
        if match:
            res = try_parse(match.group(1))
            if res: return res

        # 3. 구조적 추출 (balanced braces 기반 중첩 JSON 처리)
        def extract_balanced(text):
            stack = []
            start = -1
            for i, char in enumerate(text):
                if char == '{':
                    if not stack:
                        start = i
                    stack.append('{')
                elif char == '}':
                    if stack:
                        stack.pop()
                        if not stack and start != -1:
                            # 밸런스가 맞음, 파싱 시도
                            candidate = text[start : i + 1]
                            res = try_parse(candidate)
                            if res: return res
            return None

        res = extract_balanced(response_text)
        if res: return res

        logger.error(f"Failed to parse Claude response. Raw text snippet: {response_text[:100]}...")
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
