import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("ConsensusEngine")

class ConsensusEngine:
    """
    Gemini(1차 분석)와 Claude(2차 심층 분석) 결과를 종합하여
    최종 투자 판단 및 상태를 결정한다.
    """
    
    @staticmethod
    def analyze(gemini_result: Dict[str, Any], claude_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gemini와 Claude 결과를 종합하여 Consensus를 도출한다.
        """
        g_dec = gemini_result.get("decision")
        c_eval = claude_result.get("evaluation") # PASS, WARNING, REJECT
        
        # 1. Decision 도출 로직 (예시)
        # Gemini는 BUY/SELL/HOLD, Claude는 PASS/WARNING/REJECT
        # 여기서는 단순화하여 Claude의 의견을 반영한 최종 decision을 결정한다.
        
        final_decision = g_dec # 기본값
        status = "AGREEMENT" # 기본값
        conflicts = []
        
        # Conflict 감지 예시
        if g_dec == "BUY" and c_eval == "REJECT":
            final_decision = "HOLD"
            status = "CONFLICT"
            conflicts.append("Gemini는 BUY이나 Claude는 강력한 REJECT 의견 제시.")
        elif g_dec == "BUY" and c_eval == "WARNING":
            final_decision = "HOLD"
            status = "REVIEW"
            conflicts.append("Gemini는 BUY이나 Claude는 WARNING 의견 제시.")
            
        # 2. 결과 종합 구조화
        consensus = {
            "decision": final_decision,
            "confidence": (gemini_result.get("confidence", 0) + (claude_result.get("score", 0)/100)) / 2,
            "status": status,
            "gemini": gemini_result,
            "claude": claude_result,
            "conflicts": conflicts,
            "reasoning": f"Gemini decision: {g_dec}, Claude evaluation: {c_eval}. Status: {status}"
        }
        
        return consensus
