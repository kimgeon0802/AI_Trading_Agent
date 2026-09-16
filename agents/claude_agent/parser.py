import json
import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger("ClaudeParser")

class ClaudeParser:
    @staticmethod
    def parse_response(response_text: str) -> Optional[Dict[str, Any]]:
        """
        Claude 응답을 파싱하여 JSON으로 추출하고 유효성 검증을 수행합니다.
        강력한 Markdown 및 JSON 추출 기능을 제공하며, 실패 시 상세한 디버그 로그를 남깁니다.
        """
        if not response_text:
            logger.error("Empty response text.")
            return None

        def try_parse(text):
            try:
                # 1. 시도: 직접 파싱
                data = json.loads(text.strip(), strict=False)
                if ClaudeParser._validate_schema(data):
                    return data
                else:
                    logger.error("Schema validation failed.")
                    return None
            except json.JSONDecodeError as e:
                start = max(0, e.pos - 50)
                end = min(len(text), e.pos + 50)
                logger.error(
                    f"Claude JSON parse failed: msg={e.msg}, pos={e.pos}, lineno={e.lineno}, colno={e.colno}, "
                    f"context={repr(text[start:end])}"
                )
                return None
            except (TypeError, ValueError) as e:
                logger.error(f"Claude JSON parse error (non-decode): {e}")
                return None

        # 1. 전체 텍스트 파싱 시도
        res = try_parse(response_text)
        if res: return res

        # 2. 마크다운 코드 블록 시도
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL)
        if match:
            res = try_parse(match.group(1))
            if res: return res

        # 3. 구조적 추출 (강화된 로직)
        def extract_json_robust(text):
            # JSON은 보통 {로 시작하여 }로 끝남
            # 이스케이프된 따옴표를 고려하기 위해 정규식으로 유효한 JSON object 패턴 검색
            pattern = re.compile(r'\{.*\}', re.DOTALL)
            match = pattern.search(text)
            if match:
                candidate = match.group(0)
                res = try_parse(candidate)
                if res: return res
            return None

        res = extract_json_robust(response_text)
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
            logger.error(f"Missing required fields. Required: {required}, Found: {list(data.keys())}")
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
